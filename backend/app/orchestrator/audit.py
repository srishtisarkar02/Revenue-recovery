from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class AgentActionLog(Base):
    __tablename__ = "agent_action_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int]
    action: Mapped[str]
    details: Mapped[str] = mapped_column(Text)