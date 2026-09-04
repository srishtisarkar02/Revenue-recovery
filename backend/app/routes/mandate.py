from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MandateSchedule
from app.services.mandate import MandateRetrySequencer

router = APIRouter(
    prefix="/mandate",
    tags=["Mandate & Subscription Sequencer"],
)


class MandateScheduleRequest(BaseModel):
    mandate_id: str
    customer_id: str
    amount: int = Field(gt=0)
    failure_code: str = "insufficient_funds"


@router.post("/schedule")
def schedule_mandate_retry(
    req: MandateScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Schedules an intelligent, timed mandate retry (e.g. salary cycle / optimal bank window)
    instead of an immediate naive retry.
    """
    sequencer = MandateRetrySequencer(db)
    return sequencer.schedule_retry(
        mandate_id=req.mandate_id,
        customer_id=req.customer_id,
        amount=req.amount,
        failure_code=req.failure_code,
    )


@router.post("/process")
def process_scheduled_mandates(
    db: Session = Depends(get_db),
):
    """
    Simulates executing all pending scheduled mandate retries during their optimal windows.
    """
    sequencer = MandateRetrySequencer(db)
    return sequencer.execute_scheduled_retries()


@router.get("/list")
def list_scheduled_mandates(
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(MandateSchedule)
    if status:
        query = query.filter(MandateSchedule.status == status)
    return query.order_by(MandateSchedule.id.desc()).limit(limit).all()
