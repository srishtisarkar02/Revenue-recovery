from sqlalchemy.orm import Session
from app.agent.schemas import AgentContext
from app.ai.rag import search_recovery_knowledge
from app.models import RecoveryCase
from app.orchestrator.audit import AgentActionLog


def build_case_history(db: Session, case: RecoveryCase) -> dict:
    """
    Queries persistent action logs from PostgreSQL to determine retry count,
    message count, and previous recovery success for this case and customer.
    """
    logs = (
        db.query(AgentActionLog)
        .filter(AgentActionLog.case_id == case.id)
        .all()
    )

    retry_attempts = sum(1 for log in logs if log.action == "retry_payment")
    message_attempts = sum(
        1 for log in logs if log.action == "send_recovery_message"
    )
    recovery_attempts = retry_attempts + message_attempts

    # Customer lifetime recovery record
    customer_cases = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.customer_id == case.customer_id,
            RecoveryCase.id != case.id,
        )
        .all()
    )
    previous_successful = sum(
        1 for c in customer_cases if c.status == "recovered"
    )

    return {
        "case_id": case.id,
        "previous_retry_attempts": retry_attempts,
        "previous_recovery_attempts": recovery_attempts,
        "previous_message_attempts": message_attempts,
        "previous_successful_recoveries": previous_successful,
        "total_logs_recorded": len(logs),
    }


def format_case_history(history: dict) -> str:
    """Formats history dictionary into a clear prompt block for Gemini."""
    return (
        f"Case Memory & Past Attempts:\n"
        f"- Retries Attempted on this Case: {history.get('previous_retry_attempts', 0)}\n"
        f"- Messages Sent on this Case: {history.get('previous_message_attempts', 0)}\n"
        f"- Total Recovery Interventions: {history.get('previous_recovery_attempts', 0)}\n"
        f"- Customer's Lifetime Successful Recoveries: {history.get('previous_successful_recoveries', 0)}"
    )


def build_agent_context(case_data) -> AgentContext:
    return AgentContext(
        payment_id=case_data.payment_id,
        customer_id=case_data.customer_id,
        amount=case_data.amount,
        currency=case_data.currency,
        failure_reason=case_data.failure_reason,
        previous_payment_count=getattr(
            case_data, "previous_payment_count", 0
        ),
        previous_failed_payment_count=getattr(
            case_data, "previous_failed_payment_count", 0
        ),
        previous_recovery_attempts=getattr(
            case_data, "previous_recovery_attempts", 0
        ),
        previous_retry_attempts=getattr(
            case_data, "previous_retry_attempts", 0
        ),
        previous_successful_recoveries=getattr(
            case_data, "previous_successful_recoveries", 0
        ),
        customer_value=getattr(
            case_data, "customer_value", "standard"
        ),
        risk_flags=getattr(
            case_data, "risk_flags", []
        ),
    )


def get_recovery_knowledge(failure_reason: str):
    return search_recovery_knowledge(
        failure_reason,
        limit=3,
    )