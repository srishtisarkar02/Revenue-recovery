import json

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class RecoveryKnowledgeItem(Base):
    __tablename__ = "recovery_knowledge_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200))

    failure_reason: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(100)
    )

    content: Mapped[str] = mapped_column(Text)

    # Stored as JSON for now.
    # The semantic vectors are real Gemini embeddings.
    embedding_json: Mapped[str] = mapped_column(Text)

    def set_embedding(self, values: list[float]) -> None:
        self.embedding_json = json.dumps(values)

    def get_embedding(self) -> list[float]:
        return json.loads(self.embedding_json)


RECOVERY_KNOWLEDGE = [
    {
        "key": "network-transient-retry",
        "title": "Transient network failure recovery",
        "failure_reason": "network_error",
        "recommended_action": "retry_payment",
        "content": (
            "Network errors are usually transient. A single bounded automatic "
            "retry is appropriate when there are no fraud signals. Verify the "
            "payment after retrying. Do not retry indefinitely."
        ),
    },
    {
        "key": "timeout-retry",
        "title": "Gateway timeout recovery",
        "failure_reason": "timeout",
        "recommended_action": "retry_payment",
        "content": (
            "Gateway and connection timeouts can be temporary infrastructure "
            "failures. Retry only within the configured retry budget and "
            "independently verify the resulting payment state."
        ),
    },
    {
        "key": "gateway-timeout-retry",
        "title": "Gateway timeout handling",
        "failure_reason": "gateway_timeout",
        "recommended_action": "retry_payment",
        "content": (
            "A gateway timeout may be transient. Prefer one bounded retry when "
            "there are no risk flags. Never infer success from the retry call; "
            "verify payment status afterwards."
        ),
    },
    {
        "key": "insufficient-funds-message",
        "title": "Insufficient funds recovery",
        "failure_reason": "insufficient_funds",
        "recommended_action": "send_recovery_message",
        "content": (
            "Insufficient funds normally requires customer action. Repeated "
            "immediate retries are unlikely to help. Send a concise recovery "
            "message asking the customer to retry after adding funds or to use "
            "another payment method."
        ),
    },
    {
        "key": "bank-declined-message",
        "title": "Bank declined payment",
        "failure_reason": "bank_declined",
        "recommended_action": "send_recovery_message",
        "content": (
            "For a bank-declined payment, avoid aggressive automatic retries "
            "unless evidence suggests the decline is temporary. Ask the "
            "customer to retry or use an alternative payment method."
        ),
    },
    {
        "key": "expired-card-update",
        "title": "Expired card recovery",
        "failure_reason": "expired_card",
        "recommended_action": "send_recovery_message",
        "content": (
            "An expired card cannot be fixed through repeated retries. Prompt "
            "the customer to update the payment method. Stop automatic retry "
            "attempts against the expired instrument."
        ),
    },
    {
        "key": "fraud-human-review",
        "title": "Fraud-risk escalation",
        "failure_reason": "suspected_fraud",
        "recommended_action": "escalate",
        "content": (
            "Fraud indicators require human or dedicated risk review. Do not "
            "automatically retry or contact the customer with instructions "
            "that could bypass risk controls."
        ),
    },
    {
        "key": "chargeback-review",
        "title": "Chargeback escalation",
        "failure_reason": "chargeback",
        "recommended_action": "escalate",
        "content": (
            "Chargeback-related cases must not be handled as ordinary payment "
            "recovery. Escalate for review and preserve an audit trail."
        ),
    },
    {
        "key": "retry-budget-stop",
        "title": "Retry stopping rule",
        "failure_reason": "repeated_failure",
        "recommended_action": "escalate",
        "content": (
            "Once the configured retry budget is exhausted, stop automatic "
            "payment retries. Escalate or choose a non-retry intervention. "
            "Repeated attempts create customer and operational risk."
        ),
    },
    {
        "key": "contact-budget-stop",
        "title": "Customer contact stopping rule",
        "failure_reason": "repeated_contact",
        "recommended_action": "no_action",
        "content": (
            "Do not repeatedly contact a customer after the recovery contact "
            "budget is exhausted. Stop additional automated messages and "
            "escalate when appropriate."
        ),
    },
    {
        "key": "already-recovered-stop",
        "title": "Recovered payment stopping rule",
        "failure_reason": "already_recovered",
        "recommended_action": "no_action",
        "content": (
            "Once payment recovery has been independently verified, no further "
            "recovery action should execute. Subsequent duplicate events must "
            "be treated idempotently."
        ),
    },
    {
        "key": "high-value-caution",
        "title": "High-value payment caution",
        "failure_reason": "high_value",
        "recommended_action": "escalate",
        "content": (
            "High-value transactions deserve stronger safeguards. Avoid "
            "aggressive automatic money movement when risk or repeated failure "
            "exists. Prefer human review when uncertainty is material."
        ),
    },
]