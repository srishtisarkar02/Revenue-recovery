from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecoveryCase
from app.orchestrator.audit import AgentActionLog
from app.schemas import PaymentFailureEvent, RecoveryCaseResponse
from app.services.recovery import create_recovery_case
from app.simulator.shared import simulator
from app.tools.razorpay_tools import razorpay_client

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/payment-failed",
    response_model=RecoveryCaseResponse,
)
def payment_failed(
    event: PaymentFailureEvent,
    db: Session = Depends(get_db),
):
    return create_recovery_case(
        db=db,
        customer_id=event.customer_id,
        payment_id=event.payment_id,
        amount=event.amount,
    )


@router.post("/razorpay-webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(default=None),
):
    """
    Ingests live or simulated Razorpay webhooks (e.g., payment.failed, payment_link.paid).
    Automatically creates recovery cases or verifies successful recoveries.
    """
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8")

    # Verify signature if present
    if x_razorpay_signature and not razorpay_client.verify_webhook_signature(body_text, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event", "payment.failed")
    event_payload = payload.get("payload", {})

    if event_type == "payment.failed":
        payment_entity = event_payload.get("payment", {}).get("entity", {})
        payment_id = payment_entity.get("id", payload.get("payment_id", f"pay_rzp_{uuid_short()}"))
        customer_id = payment_entity.get("customer_id", payload.get("customer_id", "cust_rzp_demo"))
        amount = payment_entity.get("amount", payload.get("amount", 250000)) // 100 or 2500
        error_desc = payment_entity.get("error_description", payload.get("error_description", "Payment failed at gateway"))
        error_reason = payment_entity.get("error_reason", payload.get("failure_reason", "gateway_timeout"))

        # Register in simulator
        try:
            simulator.get_payment(payment_id)
        except ValueError:
            simulator.add_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                currency="INR",
                failure_reason=error_reason,
            )

        case = create_recovery_case(
            db=db,
            customer_id=customer_id,
            payment_id=payment_id,
            amount=amount,
        )

        return {
            "status": "case_created",
            "event": event_type,
            "case_id": case.id,
            "payment_id": payment_id,
            "amount": amount,
            "reason": error_desc,
        }

    elif event_type in {"payment_link.paid", "payment.captured", "order.paid"}:
        link_entity = event_payload.get("payment_link", {}).get("entity", {})
        payment_id = link_entity.get("reference_id", payload.get("payment_id"))

        if payment_id:
            case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment_id).first()
            if case:
                case.status = "recovered"
                log = AgentActionLog(
                    case_id=case.id,
                    action="payment_link_paid",
                    details=f"Payment recovered via Razorpay webhook ({event_type})",
                )
                db.add(log)
                db.commit()
                return {
                    "status": "case_recovered",
                    "event": event_type,
                    "case_id": case.id,
                    "payment_id": payment_id,
                }

    return {
        "status": "received",
        "event": event_type,
    }


def uuid_short() -> str:
    import uuid
    return uuid.uuid4().hex[:6]