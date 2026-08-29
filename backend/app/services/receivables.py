import os
from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import PromiseToPay
from app.orchestrator.audit import AgentActionLog

load_dotenv()


class PTPExtraction(BaseModel):
    has_promise: bool = Field(description="Whether customer made a commitment to pay")
    promised_date: str = Field(description="Extracted ISO promised payment date, or estimated date")
    intent_summary: str = Field(description="Summary of customer response and reason for delay")
    recommended_action: str = Field(description="pause_reminders, follow_up_immediately, or escalate_dispute")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


class ReceivablesTracker:
    """
    B2B Receivables & Promise-to-Pay (PTP) Tracker.
    Parses conversational replies, sets promise deadlines, and prevents aggressive friction.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = os.getenv("RECOVERY_AGENT_MODEL", "gemini-3.6-flash")

    def analyze_response(self, customer_message: str, amount: int) -> PTPExtraction:
        """
        Uses Gemini to extract promise-to-pay date and customer sentiment from messages.
        """
        prompt = f"""
Analyze this B2B customer response regarding an overdue payment/invoice of INR {amount}:
Customer message: "{customer_message}"

Extract:
1. Has the customer committed or promised to pay? (true/false)
2. What is the promised date or timeframe? (e.g. 2026-09-04 or YYYY-MM-DD)
3. Brief summary of intent
4. Recommended action: 'pause_reminders', 'follow_up_immediately', or 'escalate_dispute'
"""
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=PTPExtraction,
                        temperature=0.1,
                    ),
                )
                if response.text:
                    return PTPExtraction.model_validate_json(response.text)
            except Exception:
                pass

        # Deterministic fallback
        msg = customer_message.lower()
        now = datetime.now()
        if any(k in msg for k in ["friday", "tomorrow", "next week", "clearing", "transferring", "will pay", "processing"]):
            promised = (now + timedelta(days=4)).strftime("%Y-%m-%d")
            return PTPExtraction(
                has_promise=True,
                promised_date=promised,
                intent_summary="Customer acknowledged invoice and committed to settle in a few days.",
                recommended_action="pause_reminders",
                confidence=0.92,
            )
        elif any(k in msg for k in ["dispute", "wrong", "incorrect", "gst", "query"]):
            return PTPExtraction(
                has_promise=False,
                promised_date="",
                intent_summary="Customer has a dispute/query regarding invoice details.",
                recommended_action="escalate_dispute",
                confidence=0.95,
            )
        else:
            return PTPExtraction(
                has_promise=False,
                promised_date="",
                intent_summary="Ambiguous response without clear payment commitment.",
                recommended_action="follow_up_immediately",
                confidence=0.75,
            )

    def record_promise_to_pay(
        self,
        *,
        invoice_id: str,
        customer_id: str,
        amount: int,
        customer_message: str,
    ) -> dict[str, Any]:
        """
        Processes message, updates PTP state, and pauses aggressive reminders.
        """
        analysis = self.analyze_response(customer_message, amount)

        ptp = PromiseToPay(
            invoice_id=invoice_id,
            customer_id=customer_id,
            amount=amount,
            currency="INR",
            promised_date=analysis.promised_date or (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            customer_message=customer_message,
            status="active" if analysis.has_promise else "uncommitted",
            follow_up_scheduled=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        )
        self.db.add(ptp)
        self.db.commit()
        self.db.refresh(ptp)

        # Audit log
        action_name = "ptp_commitment_recorded" if analysis.has_promise else "ptp_review_needed"
        log = AgentActionLog(
            case_id=ptp.id,
            action=action_name,
            details=f"Invoice {invoice_id} (₹{amount}). Action: {analysis.recommended_action}. Promised: {ptp.promised_date}. Note: {analysis.intent_summary}",
        )
        self.db.add(log)
        self.db.commit()

        return {
            "ptp_id": ptp.id,
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount": amount,
            "has_promise": analysis.has_promise,
            "promised_date": ptp.promised_date,
            "action_taken": analysis.recommended_action,
            "intent_summary": analysis.intent_summary,
            "status": ptp.status,
            "reminders_paused": analysis.recommended_action == "pause_reminders",
        }
