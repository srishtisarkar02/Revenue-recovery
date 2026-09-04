import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:sylvia12@localhost:5432/revenue_recovery",
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    connect_args = {}
    if "sqlite" in DATABASE_URL:
        connect_args = {"check_same_thread": False}
    elif "postgresql" in DATABASE_URL:
        connect_args = {"connect_timeout": 4}

    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    with engine.connect() as conn:
        pass
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
except Exception:
    import tempfile
    fallback_db = os.path.join(tempfile.gettempdir(), "recovery_demo.db")
    engine = create_engine(f"sqlite:///{fallback_db}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


        