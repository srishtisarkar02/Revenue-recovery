from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.policy.evaluator import (
    PolicyContext,
    evaluate_policy,
)


router = APIRouter(
    prefix="/policy",
    tags=["Policy"],
)


class PolicyCheckRequest(BaseModel):
    decision: str

    amount: int = Field(gt=0)

    failure_reason: str

    previous_recovery_attempts: int = Field(
        default=0,
        ge=0,
    )

    previous_retry_attempts: int = Field(
        default=0,
        ge=0,
    )

    risk_flags: list[str] = Field(
        default_factory=list,
    )


@router.post("/check")
def check_policy(
    request: PolicyCheckRequest,
):
    result = evaluate_policy(
        decision=request.decision,
        context=PolicyContext(
            amount=request.amount,
            failure_reason=request.failure_reason,
            previous_recovery_attempts=request.previous_recovery_attempts,
            previous_retry_attempts=request.previous_retry_attempts,
            risk_flags=request.risk_flags,
        ),
    )

    return {
        "allowed": result.allowed,
        "decision": result.decision,
        "reason": result.reason,
        "violated_rules": result.violated_rules,
    }