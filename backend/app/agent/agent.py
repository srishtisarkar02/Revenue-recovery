import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.agent.prompts import SYSTEM_PROMPT, build_case_prompt
from app.agent.schemas import AgentContext, AgentDecisionResponse
from app.ai.rag import search_recovery_knowledge

load_dotenv()



class RecoveryAgent:
    """
    AI reasoning layer powered by Google Gemini and RAG policies.

    Flow:
    Case Context + Memory + RAG
      ↓
    Gemini Structured Reasoning
      ↓
    Safe Action Recommendation
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
        # Prioritized list of candidate models
        env_model = os.getenv("RECOVERY_AGENT_MODEL")
        candidates = [env_model, "gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]
        self.candidate_models = [m for m in candidates if m]

    def decide(
        self,
        context: AgentContext,
        knowledge_context: str | None = None,
        history_context: str | None = None,
    ) -> AgentDecisionResponse:
        # 1. Retrieve knowledge if not explicitly passed
        recovery_knowledge = None
        if not knowledge_context:
            recovery_knowledge = search_recovery_knowledge(
                context.failure_reason,
                limit=3,
            )

        # 2. Build Gemini prompt
        prompt = build_case_prompt(
            context=context,
            recovery_knowledge=recovery_knowledge,
            knowledge_context=knowledge_context,
            history_context=history_context,
        )

        # 3. Call Gemini across candidate models
        last_error = None
        if self.client:
            for model_name in self.candidate_models:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[
                            SYSTEM_PROMPT,
                            prompt,
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AgentDecisionResponse,
                            temperature=0.1,
                        ),
                    )
                    if response.text:
                        return AgentDecisionResponse.model_validate_json(response.text)
                except Exception as exc:
                    last_error = exc
                    continue

        # 4. Deterministic reasoning fallback if API unavailable or quota reached
        return self._fallback_decision(context, last_error)

    def _fallback_decision(self, context: AgentContext, last_error: Exception | None) -> AgentDecisionResponse:
        """Deterministic safety-aware reasoning fallback."""
        failure = context.failure_reason.lower().strip()
        risk_flags = [f.lower().strip() for f in context.risk_flags]

        if any(f in {"fraud", "suspected_fraud", "chargeback", "stolen_card"} for f in [failure] + risk_flags):
            return AgentDecisionResponse(
                decision="escalate",
                confidence=0.98,
                reason=f"Security risk flag detected ({failure}). Automated recovery is unsafe. Escalate to operations.",
                customer_message="",
                next_step="Escalate to fraud operations queue.",
            )

        if context.previous_retry_attempts >= 2:
            return AgentDecisionResponse(
                decision="escalate",
                confidence=0.95,
                reason=f"Maximum retry limit of 2 attempts reached. Stopping automated retries to prevent customer friction.",
                customer_message="",
                next_step="Hand over to manual customer support.",
            )

        if failure in {"network_error", "timeout", "gateway_timeout", "temporary_failure", "connection_error"}:
            return AgentDecisionResponse(
                decision="retry_payment",
                confidence=0.92,
                reason=f"Transient infrastructure failure ({failure}). Recovery policy recommends an automated bounded retry.",
                customer_message="",
                next_step="Execute automated retry and independently verify status.",
            )

        if failure in {"insufficient_funds", "bank_declined", "expired_card", "payment_failed"}:
            return AgentDecisionResponse(
                decision="send_recovery_message",
                confidence=0.90,
                reason=f"Customer-side decline ({failure}). Recommending 1-click Razorpay payment recovery link.",
                customer_message=f"Your payment of INR {context.amount} could not be processed due to {context.failure_reason}. Please retry using the secure payment link.",
                next_step="Send recovery notification with Razorpay payment link.",
            )

        return AgentDecisionResponse(
            decision="escalate",
            confidence=0.80,
            reason=f"Unrecognized failure reason ({failure}). Escalate for human assessment.",
            customer_message="",
            next_step="Review failure logs.",
        )



def get_agent() -> RecoveryAgent:
    return RecoveryAgent()