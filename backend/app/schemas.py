from enum import Enum
from pydantic import BaseModel


class RecoveryCaseCreate(BaseModel):
    customer_id: str
    payment_id: str
    amount: int


class RecoveryCaseResponse(BaseModel):
    id: int
    customer_id: str
    payment_id: str
    amount: int
    currency: str
    status: str

    model_config = {"from_attributes": True}


class RecoveryStatus(str, Enum):
    OPEN = "open"
    RECOVERED = "recovered"
    FAILED = "failed"
    ESCALATED = "escalated"

class PaymentFailureEvent(BaseModel):
    payment_id: str
    customer_id: str
    amount: int
    reason: str
class RecoveryCaseUpdate(BaseModel):
    status: RecoveryStatus

class RecoveryActionResponse(BaseModel):
    case_id: int
    action: str
    customer_id: str
    payment_id: str
    message: str
    status: str