from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecoveryCase
from app.orchestrator.recovery import RecoveryOrchestrator
from app.simulator.shared import simulator

router = APIRouter(
    prefix="/orchestrator",
    tags=["Recovery Orchestrator"],
)


class RunRecoveryRequest(BaseModel):
    failure_reason: str | None = None
    failure_category: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    intended_outcome: str | None = None


@router.post("/run/{case_id}")
def run_recovery(
    case_id: int,
    req: RunRecoveryRequest | None = None,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == case_id)
        .first()
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found.",
        )

    try:
        simulator.get_payment(case.payment_id)
        if req and req.failure_reason:
            simulator.payments[case.payment_id].failure_reason = req.failure_reason
        if req and req.failure_category:
            simulator.payments[case.payment_id].failure_category = req.failure_category
        if req and req.customer_name:
            simulator.payments[case.payment_id].customer_name = req.customer_name
        if req and req.customer_email:
            simulator.payments[case.payment_id].customer_email = req.customer_email
    except ValueError:
        effective_reason = "network_error"
        if req and req.failure_reason:
            effective_reason = req.failure_reason
        elif req and req.failure_category:
            effective_reason = req.failure_category

        simulator.add_payment(
            payment_id=case.payment_id,
            customer_id=case.customer_id,
            amount=case.amount,
            currency=case.currency,
            failure_reason=effective_reason,
            failure_category=req.failure_category if req else None,
            customer_name=req.customer_name if req else None,
            customer_email=req.customer_email if req else None,
        )

    orchestrator = RecoveryOrchestrator(
        db=db,
        simulator=simulator,
    )

    try:
        return orchestrator.run(case)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Recovery orchestration failed: {str(exc)}",
        ) from exc
