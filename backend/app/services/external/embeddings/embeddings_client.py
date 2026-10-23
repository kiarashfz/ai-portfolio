from openai import AsyncOpenAI


class EmbeddingsClient:
    def __init__(self, base_url: str, api_key: str, model: str = "text-embedding-3-small"):
        # AsyncOpenAI — never blocks the event loop
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=text.strip(),
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        cleaned = [t.strip() for t in texts if t.strip()]
        response = await self.client.embeddings.create(
            model=self.model,
            input=cleaned,
        )
        return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]