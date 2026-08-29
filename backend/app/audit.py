from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int]
    action: Mapped[str] = mapped_column(String(100))
    details: Mapped[str] = mapped_column(Text)