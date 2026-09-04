from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecoveryCase
from app.orchestrator.audit import AgentActionLog
from app.tools.razorpay_tools import razorpay_client

router = APIRouter(
    prefix="/razorpay",
    tags=["Razorpay Payment Gateway"],
)


class CreateOrderRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in INR")
    currency: str = "INR"
    receipt: str = Field(description="Receipt ID / Payment ID")
    customer_id: str | None = "cust_recovery"
    case_id: int | None = None


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    case_id: int | None = None
    payment_id: str | None = None


class CreatePaymentLinkRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in INR")
    currency: str = "INR"
    customer_id: str = "cust_recovery"
    payment_id: str
    description: str = "Invoice Revenue Recovery Link"


@router.get("/config")
def get_razorpay_config():
    """Returns the public Razorpay Key ID for frontend Checkout.js integration."""
    return {
        "key_id": razorpay_client.key_id,
        "currency": "INR",
        "name": "RecoveryOS Control Plane",
    }


@router.get("/status")
def get_razorpay_status():
    """Returns real-time connection status of Razorpay integration."""
    return razorpay_client.get_status()


@router.post("/create-order")
def create_checkout_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_db),
):
    """
    Creates a REAL Razorpay Order via REST API for standard Checkout.js popup integration.
    Raises HTTP 502 with clear error if Razorpay API cannot be reached or credentials fail.
    """
    try:
        order = razorpay_client.create_order(
            amount=req.amount,
            currency=req.currency,
            receipt=req.receipt,
            notes={"customer_id": req.customer_id or "cust_default"},
            case_id=req.case_id,
        )
        return {
            "key_id": order["key_id"],
            "order_id": order["order_id"],
            "id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "receipt": order["receipt"],
            "status": order["status"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Razorpay Test Mode unavailable: {str(e)}",
        )


@router.post("/create-payment-link")
def create_payment_link(
    req: CreatePaymentLinkRequest,
    db: Session = Depends(get_db),
):
    """
    Generates an official Razorpay Test Mode Payment Link via REST API.
    """
    try:
        link = razorpay_client.create_payment_link(
            amount=req.amount,
            currency=req.currency,
            customer_id=req.customer_id,
            payment_id=req.payment_id,
            description=req.description,
        )
        return link
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Razorpay Test Mode unavailable: {str(e)}",
        )


class CheckoutFailedRequest(BaseModel):
    order_id: str
    payment_id: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    error_source: str | None = None
    error_step: str | None = None
    error_reason: str | None = None
    case_id: int | None = None
    amount: int | None = None
    customer_id: str | None = None


@router.post("/checkout-failed")
def handle_checkout_failed(
    req: CheckoutFailedRequest,
    db: Session = Depends(get_db),
):
    """
    Receives real payment.failed events from official Razorpay Checkout.js.
    Maps error codes to failure categories and runs the existing 7-step RecoveryOrchestrator.
    """
    from app.orchestrator.recovery import RecoveryOrchestrator
    from app.simulator.shared import simulator

    # 1. Map Razorpay error to internal failure reason
    raw = f"{req.error_reason or ''} {req.error_code or ''} {req.error_description or ''}".lower()
    if any(k in raw for k in ["timeout", "timed_out", "gateway", "network", "server_error"]):
        mapped_reason = "gateway_timeout"
    elif any(k in raw for k in ["insufficient", "balance", "funds", "cancelled", "user_dropped"]):
        mapped_reason = "insufficient_funds"
    elif any(k in raw for k in ["expired", "expiry"]):
        mapped_reason = "expired_card"
    elif any(k in raw for k in ["fraud", "risk", "security", "velocity", "stolen", "blacklisted"]):
        mapped_reason = "suspected_fraud"
    else:
        mapped_reason = "bank_declined"

    # 2. Match or create RecoveryCase
    case = None
    if req.case_id:
        case = db.query(RecoveryCase).filter(RecoveryCase.id == req.case_id).first()

    payment_id = req.payment_id or f"pay_rzp_fail_{req.order_id[-8:] if req.order_id else 'test'}"

    if not case:
        case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment_id).first()

    if not case:
        case = RecoveryCase(
            customer_id=req.customer_id or "cust_test_checkout",
            payment_id=payment_id,
            amount=req.amount or 3500,
            currency="INR",
            status="open",
        )
        db.add(case)
        db.commit()
        db.refresh(case)

    # 3. Add to simulator so orchestrator can evaluate and execute
    try:
        simulator.get_payment(case.payment_id)
    except ValueError:
        simulator.add_payment(
            payment_id=case.payment_id,
            customer_id=case.customer_id,
            amount=case.amount,
            currency=case.currency,
            failure_reason=mapped_reason,
        )

    # 4. Execute 7-step RecoveryOrchestrator
    orchestrator = RecoveryOrchestrator(db=db, simulator=simulator)
    result = orchestrator.run(case)

    # 5. Log audit action
    audit = AgentActionLog(
        case_id=case.id,
        action="razorpay_test_checkout_failed",
        details=(
            f"Real Razorpay Checkout failure ingested: {req.error_description or req.error_code or 'Payment Failed'}. "
            f"Mapped Failure Category: '{mapped_reason}'. "
            f"Agent Decision: {result.get('decision', {}).get('action', 'unknown')}. "
            f"Outcome: {result.get('final_status', case.status)}."
        ),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "failure_orchestrated",
        "case_id": case.id,
        "payment_id": case.payment_id,
        "amount": case.amount,
        "failure_reason": mapped_reason,
        "error_code": req.error_code,
        "error_description": req.error_description,
        "final_case_status": case.status,
        "orchestrator_summary": result,
    }


@router.post("/verify-payment")
def verify_checkout_payment(
    req: VerifyPaymentRequest,
    db: Session = Depends(get_db),
):
    """
    Verifies Razorpay standard checkout payment signature using server-stored order ID
    and marks the recovery case as recovered in PostgreSQL.
    """
    # Use server-stored order ID as source of truth when available
    server_order_id = req.razorpay_order_id
    if req.payment_id:
        stored_by_receipt = razorpay_client.get_order_by_receipt(req.payment_id)
        if stored_by_receipt:
            server_order_id = stored_by_receipt
    elif razorpay_client.get_server_order(req.razorpay_order_id):
        server_order_id = razorpay_client.get_server_order(req.razorpay_order_id)["order_id"]

    is_valid = razorpay_client.verify_payment_signature(
        order_id=server_order_id,
        payment_id=req.razorpay_payment_id,
        signature=req.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay payment signature",
        )

    # Find matching case
    case = None
    if req.case_id:
        case = db.query(RecoveryCase).filter(RecoveryCase.id == req.case_id).first()
    elif req.payment_id:
        case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == req.payment_id).first()

    if case:
        case.status = "recovered"
        db.commit()
        db.refresh(case)

        audit = AgentActionLog(
            case_id=case.id,
            action="razorpay_checkout_recovered",
            details=f"Payment verified via Razorpay Gateway. Order ID: {server_order_id}, Payment ID: {req.razorpay_payment_id}. Amount: INR {case.amount}",
        )
        db.add(audit)
        db.commit()

    return {
        "verified": True,
        "status": "recovered",
        "razorpay_order_id": server_order_id,
        "razorpay_payment_id": req.razorpay_payment_id,
        "case_id": case.id if case else None,
        "message": "Payment successfully verified and revenue recovered via Razorpay Gateway.",
    }



