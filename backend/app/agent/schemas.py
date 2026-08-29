from typing import Literal

from pydantic import BaseModel, Field


AgentDecision = Literal[
    "retry_payment",
    "send_recovery_message",
    "escalate",
    "no_action",
]


class AgentDecisionResponse(BaseModel):
    decision: AgentDecision
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    reason: str = Field(
        min_length=1,
        max_length=1000,
    )
    customer_message: str = Field(
        default="",
        max_length=500,
    )
    next_step: str = Field(
        min_length=1,
        max_length=200,
    )


class AgentContext(BaseModel):
    payment_id: str
    customer_id: str
    amount: int
    currency: str = "INR"

    failure_reason: str

    previous_payment_count: int = 0
    previous_failed_payment_count: int = 0
    previous_recovery_attempts: int = 0
    previous_retry_attempts: int = 0
    previous_successful_recoveries: int = 0

    customer_value: str = "standard"

    risk_flags: list[str] = Field(default_factory=list)