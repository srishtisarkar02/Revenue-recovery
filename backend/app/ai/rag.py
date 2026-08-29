import json
import math
import os
from typing import Any
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.knowledge.rec_policy import RECOVERY_KNOWLEDGE, RecoveryKnowledgeItem

load_dotenv()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class RecoveryRAG:
    """
    RAG engine for payment recovery policies.
    Generates semantic embeddings via Gemini and searches recovery knowledge.
    """

    def __init__(self, db: Session | None = None) -> None:
        self.db = db
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def get_embedding(self, text: str) -> list[float]:
        """Generate vector embedding using Gemini API with deterministic fallback."""
        if self.client:
            try:
                response = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text,
                )
                if response.embeddings and len(response.embeddings) > 0:
                    return list(response.embeddings[0].values)
            except Exception:
                pass

        # Deterministic lightweight 64-dim fallback representation
        words = text.lower().split()
        vector = [0.0] * 64
        for word in words:
            idx = sum(ord(c) for c in word) % 64
            vector[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def seed_knowledge(self) -> int:
        """Seed RECOVERY_KNOWLEDGE items into PostgreSQL with embeddings."""
        session = self.db or SessionLocal()
        should_close = self.db is None

        try:
            created_count = 0
            for item in RECOVERY_KNOWLEDGE:
                existing = (
                    session.query(RecoveryKnowledgeItem)
                    .filter(RecoveryKnowledgeItem.key == item["key"])
                    .first()
                )

                embed_text = f"{item['title']}. {item['failure_reason']}. {item['recommended_action']}. {item['content']}"
                embedding = self.get_embedding(embed_text)

                if existing:
                    existing.title = item["title"]
                    existing.failure_reason = item["failure_reason"]
                    existing.recommended_action = item["recommended_action"]
                    existing.content = item["content"]
                    existing.set_embedding(embedding)
                else:
                    knowledge_item = RecoveryKnowledgeItem(
                        key=item["key"],
                        title=item["title"],
                        failure_reason=item["failure_reason"],
                        recommended_action=item["recommended_action"],
                        content=item["content"],
                    )
                    knowledge_item.set_embedding(embedding)
                    session.add(knowledge_item)
                    created_count += 1

            session.commit()
            return created_count
        finally:
            if should_close:
                session.close()

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """Perform semantic search against stored recovery knowledge."""
        session = self.db or SessionLocal()
        should_close = self.db is None

        try:
            items = session.query(RecoveryKnowledgeItem).all()
            if not items:
                # If table is empty, auto-seed first
                self.seed_knowledge()
                items = session.query(RecoveryKnowledgeItem).all()

            query_vec = self.get_embedding(query)
            results = []

            for item in items:
                try:
                    item_vec = item.get_embedding()
                except Exception:
                    continue

                similarity = cosine_similarity(query_vec, item_vec)
                results.append({
                    "id": item.id,
                    "key": item.key,
                    "title": item.title,
                    "failure_reason": item.failure_reason,
                    "recommended_action": item.recommended_action,
                    "content": item.content,
                    "similarity": round(float(similarity), 4),
                })

            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
        finally:
            if should_close:
                session.close()

    def build_recovery_context(
        self,
        failure_reason: str,
        amount: int = 0,
        currency: str = "INR",
        previous_retry_attempts: int = 0,
        previous_recovery_attempts: int = 0,
        risk_flags: list[str] | None = None,
    ) -> str:
        """Retrieve relevant recovery knowledge and format as clean text for prompts."""
        query = f"Payment failure: {failure_reason}. Amount: {amount} {currency}."
        if risk_flags:
            query += f" Risk flags: {', '.join(risk_flags)}."

        retrieved = self.search(query=query, limit=3)
        if not retrieved:
            return "No specific recovery policy found."

        context_lines = ["Relevant Recovery Policies (RAG):"]
        for idx, doc in enumerate(retrieved, 1):
            context_lines.append(
                f"{idx}. [{doc['title']}] (Similarity: {doc['similarity']})\n"
                f"   - Failure Reason: {doc['failure_reason']}\n"
                f"   - Recommended Action: {doc['recommended_action']}\n"
                f"   - Guidance: {doc['content']}"
            )

        return "\n\n".join(context_lines)


def search_recovery_knowledge(query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Helper function for backward compatibility."""
    rag = RecoveryRAG()
    return rag.search(query=query, limit=limit)