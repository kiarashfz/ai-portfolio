from __future__ import annotations
from typing import Any
from uuid import UUID

from services.external.vector_db import MilvusVectorStore
from services.external.embeddings.embeddings_client import EmbeddingsClient

RELEVANCE_THRESHOLD = 0.1


class RAGService:
    def __init__(self, vector_store: MilvusVectorStore, embeddings_client: EmbeddingsClient):
        self.vector_store = vector_store
        self.embeddings_client = embeddings_client

    async def ingest_portfolio_data(
        self,
        portfolio_id: UUID,
        portfolio_data: dict[str, Any],
        chunk_size: int = 512,
    ) -> dict[str, int]:
        # Delete stale vectors so old data doesn't pollute retrieval
        await self.vector_store.delete_portfolio_vectors(portfolio_id)

        chunks = self._build_chunks(portfolio_data, chunk_size)
        if not chunks:
            return {"chunks_created": 0, "vectors_upserted": 0}

        texts = [c["text"] for c in chunks]
        embeddings = await self.embeddings_client.embed_batch(texts)

        vectors: list[tuple[str, list[float], dict]] = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append((
                f"{portfolio_id}_{chunk['id']}",
                embedding,
                {
                    "field": chunk["field"],
                    "content": chunk["content"],
                },
            ))

        await self.vector_store.upsert_vectors(portfolio_id, vectors)
        return {"chunks_created": len(chunks), "vectors_upserted": len(vectors)}

    async def retrieve_context(
        self,
        portfolio_id: UUID,
        query: str,
        top_k: int = 3,
    ) -> str | None:
        query_embedding = await self.embeddings_client.embed(query)
        results = await self.vector_store.query(
            query_embedding=query_embedding,
            portfolio_id=portfolio_id,
            top_k=top_k,
        )

        relevant = [r for r in results if r.get("score", 0) >= RELEVANCE_THRESHOLD]
        if not relevant:
            return None

        parts = []
        for r in relevant:
            meta = r.get("metadata", {})
            field = meta.get("field", "")
            content = meta.get("content", "")
            if field and content:
                parts.append(f"{field}: {content}")
            elif content:
                parts.append(content)

        return "\n\n".join(parts) if parts else None

    async def delete_portfolio_data(self, portfolio_id: UUID) -> None:
        await self.vector_store.delete_portfolio_vectors(portfolio_id)

    @staticmethod
    def _build_chunks(data: dict[str, Any], chunk_size: int) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        counter = 0

        def add_chunk(field: str, text: str) -> None:
            nonlocal counter
            text = text.strip()
            if not text:
                return
            # Split oversized text on sentence boundaries
            if len(text) <= chunk_size:
                chunks.append({
                    "id": f"chunk_{counter}",
                    "field": field,
                    "content": text,
                    "text": f"{field}: {text}",  # richer embedding input
                })
                counter += 1
                return
            sentences = text.split(". ")
            current = ""
            for sentence in sentences:
                candidate = f"{current} {sentence}." if current else f"{sentence}."
                if len(candidate) > chunk_size and current:
                    chunks.append({
                        "id": f"chunk_{counter}",
                        "field": field,
                        "content": current.strip(),
                        "text": f"{field}: {current.strip()}",
                    })
                    counter += 1
                    current = f"{sentence}."
                else:
                    current = candidate
            if current.strip():
                chunks.append({
                    "id": f"chunk_{counter}",
                    "field": field,
                    "content": current.strip(),
                    "text": f"{field}: {current.strip()}",
                })
                counter += 1

        # ---- skills ----
        skills = data.get("skills", [])
        if skills:
            skill_list = ", ".join(skills) if isinstance(skills, list) else str(skills)
            add_chunk("Technical skills", skill_list)

        # ---- experiences ----
        for exp in data.get("experiences", []):
            company = exp.get("company", "")
            position = exp.get("position", "")
            start = exp.get("start_date", "")
            end = exp.get("end_date", "") or "present"
            description = exp.get("description", "")

            label = f"Work experience at {company} — {position} ({start} to {end})"
            if description:
                add_chunk(label, description)
            else:
                add_chunk("Work experience", f"{position} at {company} from {start} to {end}")

        # ---- education ----
        for edu in data.get("education", []):
            if isinstance(edu, dict):
                degree = edu.get("degree", "")
                institution = edu.get("institution", "")
                year = edu.get("year", "")
                add_chunk("Education", f"{degree} at {institution} ({year})")
            else:
                add_chunk("Education", str(edu))

        # ---- links ----
        links = data.get("links", {})
        if links:
            link_parts = [f"{k}: {v}" for k, v in links.items() if v]
            if link_parts:
                add_chunk("Online profiles and links", ", ".join(link_parts))

        return chunks