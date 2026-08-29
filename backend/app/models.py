from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[str]
    payment_id: Mapped[str] = mapped_column(String(100), unique=True)
    amount: Mapped[int]
    currency: Mapped[str]
    status: Mapped[str]


class MandateSchedule(Base):
    __tablename__ = "mandate_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    mandate_id: Mapped[str] = mapped_column(String(100), index=True)
    customer_id: Mapped[str]
    amount: Mapped[int]
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    failure_code: Mapped[str] = mapped_column(String(100))
    optimal_window: Mapped[str] = mapped_column(String(100))
    scheduled_date: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled, retried, recovered, cancelled
    retry_count: Mapped[int] = mapped_column(default=0)


class PromiseToPay(Base):
    __tablename__ = "promise_to_pays"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[str] = mapped_column(String(100), index=True)
    customer_id: Mapped[str]
    amount: Mapped[int]
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    promised_date: Mapped[str] = mapped_column(String(50))
    customer_message: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, fulfilled, defaulted
    follow_up_scheduled: Mapped[str] = mapped_column(String(50), default="")


