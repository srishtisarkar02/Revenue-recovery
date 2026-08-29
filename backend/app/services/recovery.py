from sqlalchemy.orm import Session

from app.models import RecoveryCase


def create_recovery_case(
    db: Session,
    customer_id: str,
    payment_id: str,
    amount: int,
):
    # Check if this payment already has a recovery case
    existing_case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.payment_id == payment_id)
        .first()
    )

    if existing_case:
        return existing_case

    # Create a new recovery case
    case = RecoveryCase(
        customer_id=customer_id,
        payment_id=payment_id,
        amount=amount,
        currency="INR",
        status="open",
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case