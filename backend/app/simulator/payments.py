from dataclasses import dataclass
from typing import Literal


PaymentStatus = Literal[
    "failed",
    "pending",
    "recovered",
]


@dataclass
class SimulatedPayment:
    payment_id: str
    customer_id: str
    amount: int
    currency: str
    failure_reason: str

    status: PaymentStatus = "failed"

    retry_count: int = 0
    failure_category: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None


class PaymentSimulator:
    def __init__(self) -> None:
        self.payments: dict[str, SimulatedPayment] = {}

    def add_payment(
        self,
        *,
        payment_id: str,
        customer_id: str,
        amount: int,
        currency: str,
        failure_reason: str,
        status: PaymentStatus = "failed",
        failure_category: str | None = None,
        customer_name: str | None = None,
        customer_email: str | None = None,
    ) -> SimulatedPayment:

        payment = SimulatedPayment(
            payment_id=payment_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            failure_reason=failure_reason,
            status=status,
            failure_category=failure_category,
            customer_name=customer_name,
            customer_email=customer_email,
        )

        self.payments[payment_id] = payment

        return payment

    def get_payment(
        self,
        payment_id: str,
    ) -> dict:

        payment = self.payments.get(payment_id)

        if payment is None:
            raise ValueError(
                f"Payment {payment_id} does not exist."
            )

        return {
            "payment_id": payment.payment_id,
            "customer_id": payment.customer_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "failure_reason": payment.failure_reason,
            "failure_category": getattr(payment, "failure_category", None) or payment.failure_reason,
            "customer_name": getattr(payment, "customer_name", None),
            "customer_email": getattr(payment, "customer_email", None),
            "status": payment.status,
            "retry_count": payment.retry_count,
        }


    def retry_payment(
        self,
        payment_id: str,
    ) -> dict:

        payment = self.payments.get(payment_id)

        if payment is None:
            raise ValueError(
                f"Payment {payment_id} does not exist."
            )

        if payment.status == "recovered":
            return {
                "payment_id": payment_id,
                "status": "already_recovered",
                "recovered": True,
            }

        payment.retry_count += 1

        # Deterministic simulation rules.
        #
        # Transient failures succeed on retry.
        if payment.failure_reason in {
            "network_error",
            "timeout",
            "gateway_timeout",
            "temporary_failure",
            "connection_error",
        }:
            payment.status = "recovered"

            return {
                "payment_id": payment_id,
                "status": "recovered",
                "recovered": True,
                "retry_count": payment.retry_count,
            }

        # Customer-side failures do not magically recover
        # through another retry.
        return {
            "payment_id": payment_id,
            "status": "failed",
            "recovered": False,
            "retry_count": payment.retry_count,
        }