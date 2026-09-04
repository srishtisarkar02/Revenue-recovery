from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PromiseToPay
from app.services.receivables import ReceivablesTracker

router = APIRouter(
    prefix="/receivables",
    tags=["B2B Receivables & Promise-to-Pay"],
)


class PTPRequest(BaseModel):
    invoice_id: str
    customer_id: str
    amount: int = Field(gt=0)
    customer_message: str


@router.post("/ptp")
def record_promise_to_pay(
    req: PTPRequest,
    db: Session = Depends(get_db),
):
    """
    Ingests customer reply, parses Promise-to-Pay commitments with Gemini,
    sets promise dates, and pauses aggressive payment chasers.
    """
    tracker = ReceivablesTracker(db)
    return tracker.record_promise_to_pay(
        invoice_id=req.invoice_id,
        customer_id=req.customer_id,
        amount=req.amount,
        customer_message=req.customer_message,
    )


@router.get("/list")
def list_promises_to_pay(
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(PromiseToPay)
    if status:
        query = query.filter(PromiseToPay.status == status)
    return query.order_by(PromiseToPay.id.desc()).limit(limit).all()
