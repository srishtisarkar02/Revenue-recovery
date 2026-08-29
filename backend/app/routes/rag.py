from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.ai.rag import RecoveryRAG
from app.database import get_db


router = APIRouter(
    prefix="/rag",
    tags=["Recovery RAG"],
)


@router.post("/seed")
def seed_recovery_knowledge(
    db: Session = Depends(get_db),
):
    rag = RecoveryRAG(db)

    created = rag.seed_knowledge()

    return {
        "status": "ready",
        "created": created,
    }


@router.get("/search")
def search_recovery_knowledge(
    query: str,
    limit: int = 3,
    db: Session = Depends(get_db),
):
    rag = RecoveryRAG(db)

    results = rag.search(
        query=query,
        limit=limit,
    )

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }