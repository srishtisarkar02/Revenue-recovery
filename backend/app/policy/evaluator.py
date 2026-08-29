from dataclasses import dataclass

from app.policy.rules import (
    BLOCKED_FAILURE_REASONS,
    HIGH_VALUE_AMOUNT,
    MAX_RECOVERY_MESSAGE_ATTEMPTS,
    MAX_RETRY_ATTEMPTS,
    TRANSIENT_FAILURE_REASONS,
)


@dataclass
class PolicyContext:
    amount: int
    failure_reason: str

    previous_recovery_attempts: int = 0
    previous_retry_attempts: int = 0

    risk_flags: list[str] | None = None


@dataclass
class PolicyResult:
    allowed: bool
    decision: str
    reason: str
    violated_rules: list[str]


def evaluate_policy(
    decision: str,
    context: PolicyContext,
) -> PolicyResult:

    failure_reason = (
        context.failure_reason
        .lower()
        .strip()
    )

    risk_flags = {
        flag.lower().strip()
        for flag in (context.risk_flags or [])
    }

    violations: list[str] = []

    # ---------------------------------------------------------
    # RULE 1 — Fraud / chargeback safety
    # ---------------------------------------------------------

    if (
        failure_reason in BLOCKED_FAILURE_REASONS
        or risk_flags.intersection(BLOCKED_FAILURE_REASONS)
    ):
        violations.append(
            "fraud_or_chargeback_requires_human_review"
        )

    # ---------------------------------------------------------
    # RULE 2 — High-value payments
    # ---------------------------------------------------------

    if context.amount >= HIGH_VALUE_AMOUNT:
        if decision == "retry_payment":
            violations.append(
                "high_value_payment_cannot_be_automatically_retried"
            )

    # ---------------------------------------------------------
    # RULE 3 — Retry limit
    # ---------------------------------------------------------

    if decision == "retry_payment":

        if context.previous_retry_attempts >= MAX_RETRY_ATTEMPTS:
            violations.append(
                "maximum_retry_attempts_reached"
            )

        if failure_reason not in TRANSIENT_FAILURE_REASONS:
            violations.append(
                "failure_reason_is_not_safely_retryable"
            )

    # ---------------------------------------------------------
    # RULE 4 — Customer messaging limit
    # ---------------------------------------------------------

    if decision == "send_recovery_message":

        if (
            context.previous_recovery_attempts
            >= MAX_RECOVERY_MESSAGE_ATTEMPTS
        ):
            violations.append(
                "maximum_recovery_message_attempts_reached"
            )

    # ---------------------------------------------------------
    # RULE 5 — Risk flags
    # ---------------------------------------------------------

    if risk_flags:
        if decision in {
            "retry_payment",
            "send_recovery_message",
        }:
            violations.append(
                "risk_flags_require_additional_review"
            )

    # ---------------------------------------------------------
    # Final decision
    # ---------------------------------------------------------

    if violations:
        return PolicyResult(
            allowed=False,
            decision="escalate",
            reason=(
                "AI recommendation was blocked by deterministic "
                "safety policy."
            ),
            violated_rules=violations,
        )

    return PolicyResult(
        allowed=True,
        decision=decision,
        reason="AI recommendation passed all safety checks.",
        violated_rules=[],
    )