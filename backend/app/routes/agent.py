from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.agent import get_agent
from app.agent.schemas import AgentContext, AgentDecisionResponse


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


class AgentDecisionRequest(BaseModel):
    payment_id: str
    customer_id: str

    amount: int = Field(gt=0)
    currency: str = "INR"

    failure_reason: str

    previous_payment_count: int = Field(
        default=0,
        ge=0,
    )

    previous_failed_payment_count: int = Field(
        default=0,
        ge=0,
    )

    previous_recovery_attempts: int = Field(
        default=0,
        ge=0,
    )

    previous_retry_attempts: int = Field(
        default=0,
        ge=0,
    )

    previous_successful_recoveries: int = Field(
        default=0,
        ge=0,
    )

    customer_value: str = "standard"

    risk_flags: list[str] = Field(
        default_factory=list,
    )


@router.post(
    "/decide",
    response_model=AgentDecisionResponse,
)
def decide(
    request: AgentDecisionRequest,
):
    try:
        context = AgentContext(
            payment_id=request.payment_id,
            customer_id=request.customer_id,
            amount=request.amount,
            currency=request.currency,
            failure_reason=request.failure_reason,
            previous_payment_count=request.previous_payment_count,
            previous_failed_payment_count=request.previous_failed_payment_count,
            previous_recovery_attempts=request.previous_recovery_attempts,
            previous_retry_attempts=request.previous_retry_attempts,
            previous_successful_recoveries=request.previous_successful_recoveries,
            customer_value=request.customer_value,
            risk_flags=request.risk_flags,
        )

        agent = get_agent()

        return agent.decide(context)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI agent failed: {str(exc)}",
        ) from exc