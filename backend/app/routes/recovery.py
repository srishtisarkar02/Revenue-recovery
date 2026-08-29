from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.audit import AuditLog

from app.database import get_db
from app.models import RecoveryCase
from app.schemas import (
    RecoveryCaseCreate,
    RecoveryCaseResponse,
    RecoveryCaseUpdate,
    RecoveryActionResponse,
)
from app.services.recovery import create_recovery_case
from app.services.actions import send_recovery_message

router = APIRouter(prefix="/recovery", tags=["Recovery"])


@router.post("/cases", response_model=RecoveryCaseResponse)
def create_case(
    data: RecoveryCaseCreate,
    db: Session = Depends(get_db),
):
    return create_recovery_case(
        db,
        data.customer_id,
        data.payment_id,
        data.amount,
    )


@router.get("/cases", response_model=list[RecoveryCaseResponse])
def list_cases(
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(RecoveryCase)
    if status:
        query = query.filter(RecoveryCase.status == status)
    return query.order_by(RecoveryCase.id.desc()).limit(limit).all()


@router.get("/dashboard-summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    cases = db.query(RecoveryCase).all()
    total_cases = len(cases)
    total_at_risk = sum(c.amount for c in cases)
    recovered_cases = [c for c in cases if c.status == "recovered"]
    recovered_amount = sum(c.amount for c in recovered_cases)
    escalated_cases = [c for c in cases if c.status == "escalated"]
    open_cases = [c for c in cases if c.status == "open"]

    recovery_rate = round((len(recovered_cases) / total_cases) * 100, 1) if total_cases > 0 else 0.0

    return {
        "total_cases": total_cases,
        "total_revenue_at_risk_inr": total_at_risk,
        "total_revenue_recovered_inr": recovered_amount,
        "recovery_rate_percent": recovery_rate,
        "status_breakdown": {
            "recovered": len(recovered_cases),
            "escalated": len(escalated_cases),
            "open": len(open_cases),
        },
    }


@router.get("/analytics")
def get_recovery_analytics(
    db: Session = Depends(get_db),
):
    cases = db.query(RecoveryCase).all()
    total_cases = len(cases)
    recovered = [c for c in cases if c.status == "recovered"]
    escalated = [c for c in cases if c.status == "escalated"]
    open_cases = [c for c in cases if c.status == "open"]

    total_at_risk = sum(c.amount for c in cases)
    total_recovered = sum(c.amount for c in recovered)
    recovery_rate = round((len(recovered) / total_cases) * 100, 1) if total_cases > 0 else 0.0

    # Query recent logs
    from app.orchestrator.audit import AgentActionLog
    recent_logs = (
        db.query(AgentActionLog)
        .order_by(AgentActionLog.id.desc())
        .limit(20)
        .all()
    )

    return {
        "kpis": {
            "total_at_risk_inr": total_at_risk,
            "total_recovered_inr": total_recovered,
            "recovery_rate_percent": recovery_rate,
            "total_cases": total_cases,
            "recovered_count": len(recovered),
            "escalated_count": len(escalated),
            "open_count": len(open_cases),
        },
        "recent_audit_trail": [
            {
                "id": log.id,
                "case_id": log.case_id,
                "action": log.action,
                "details": log.details,
            }
            for log in recent_logs
        ],
    }


@router.get("/cases/{case_id}/audit-logs")
def get_case_audit_logs(
    case_id: int,
    db: Session = Depends(get_db),
):
    from app.orchestrator.audit import AgentActionLog
    logs = (
        db.query(AgentActionLog)
        .filter(AgentActionLog.case_id == case_id)
        .order_by(AgentActionLog.id.asc())
        .all()
    )
    return [
        {
            "id": log.id,
            "case_id": log.case_id,
            "action": log.action,
            "details": log.details,
        }
        for log in logs
    ]



@router.get("/cases/{case_id}", response_model=RecoveryCaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found",
        )

    return case


@router.patch("/cases/{case_id}", response_model=RecoveryCaseResponse)
def update_case(
    case_id: int,
    data: RecoveryCaseUpdate,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found",
        )

    case.status = data.status

    db.commit()
    db.refresh(case)

    return case


@router.post(
    "/cases/{case_id}/message",
    response_model=RecoveryActionResponse,
)
def send_message(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found",
        )

    if case.status != "open":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot send recovery message for case with status '{case.status}'",
        )
    result = send_recovery_message(
        customer_id=case.customer_id,
        payment_id=case.payment_id,
    )

    audit = AuditLog(
        case_id=case.id,
        action="send_recovery_message",
        details="Recovery message sent to customer.",
    )

    db.add(audit)
    db.commit()

    return {
        "case_id": case.id,
        **result,
    }