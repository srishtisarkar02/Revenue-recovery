from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecoveryCase

from app.orchestrator.recovery import RecoveryOrchestrator
from app.simulator.shared import simulator


router = APIRouter(
    prefix="/orchestrator",
    tags=["Recovery Orchestrator"],
)


# One simulator instance for the development environment.


@router.post("/run/{case_id}")
def run_recovery(
    case_id: int,
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

    # ---------------------------------------------------------
    # Make sure the simulator knows about this payment.
    # ---------------------------------------------------------

    try:
        simulator.get_payment(case.payment_id)

    except ValueError:

        simulator.add_payment(
            payment_id=case.payment_id,
            customer_id=case.customer_id,
            amount=case.amount,
            currency=case.currency,
            failure_reason="network_error",
        )

    # ---------------------------------------------------------
    # Run the complete agent workflow.
    # ---------------------------------------------------------

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