from uuid import UUID


class MilvusVectorStore:
    def __init__(self, host: str, port: int, collection_name: str):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    def initialize(self):
        from pymilvus import connections, Collection, MilvusClient, utility
        from pymilvus.exceptions import MilvusException

        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )

            self.client = MilvusClient(uri=f"http://{self.host}:{self.port}")

            # Drop orphaned collection that exists but has no index
            if self.client.has_collection(self.collection_name):
                col = Collection(self.collection_name, using="default")
                indexes = col.indexes
                if not indexes:
                    # Collection exists but has no index — drop and recreate
                    self.client.drop_collection(self.collection_name)
                    self._create_collection()
            else:
                self._create_collection()

            self.collection = Collection(self.collection_name, using="default")
            self.collection.load()
        except MilvusException as e:
            raise RuntimeError(
                f"Failed to connect to Milvus server at {self.host}:{self.port}. Ensure the server is running. Original error: {e}")

    def _create_collection(self):
        from pymilvus import DataType, FieldSchema, CollectionSchema, Collection, utility

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=500),
            FieldSchema(name="portfolio_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="field", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        ]

        schema = CollectionSchema(fields=fields, description="Portfolio embeddings")

        collection = Collection(
            name=self.collection_name,
            schema=schema,
            using="default",
            consistency_level="Strong",
        )

        # Create the index via the same ORM Collection object — NOT via MilvusClient
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        collection.create_index(field_name="embedding", index_params=index_params)

        # Block until the index is fully built before initialize() calls .load()
        utility.wait_for_index_building_complete(
            collection_name=self.collection_name,
            index_name="embedding",
            using="default",
        )

    async def upsert_vectors(
            self,
            portfolio_id: UUID,
            vectors: list[tuple[str, list[float], dict]],
    ) -> None:
        if not self.client:
            raise RuntimeError("Milvus client not initialized")

        data = []
        for vector_id, embedding, metadata in vectors:
            data.append({
                "id": vector_id,
                "portfolio_id": str(portfolio_id),
                "embedding": embedding,
                "field": metadata.get("field", ""),
                "content": metadata.get("content", ""),
            })

        self.client.upsert(
            collection_name=self.collection_name,
            data=data
        )

        # Flush to ensure data is persisted and visible to search
        self.collection.flush()
        # Reload the collection so the ORM search sees the new vectors
        self.collection.load()

    async def query(
        self,
        query_embedding: list[float],
        portfolio_id: UUID,
        top_k: int = 5,
    ) -> list[dict]:
        if not self.collection:
            raise RuntimeError("Milvus client not initialized")

        # Search with filter
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nlist": 128}},
            limit=top_k,
            expr=f"portfolio_id == '{str(portfolio_id)}'",  # note: expr, not filter
            output_fields=["id", "field", "content", "portfolio_id"]
        )

        formatted_results = []
        if results and len(results) > 0:
            for hit in results[0]:
                formatted_results.append({
                    "id": hit.entity.get("id"),
                    "score": hit.distance,
                    "metadata": {
                        "field": hit.entity.get("field", ""),
                        "content": hit.entity.get("content", ""),
                        "portfolio_id": hit.entity.get("portfolio_id", ""),
                    }
                })

        return formatted_results

    async def delete_portfolio_vectors(self, portfolio_id: UUID) -> None:
        if not self.client:
            raise RuntimeError("Milvus client not initialized")

        # Delete all vectors with portfolio_id filter
        self.client.delete(
            collection_name=self.collection_name,
            filter=f"portfolio_id == '{str(portfolio_id)}'"
        )

    async def delete_vectors(self, vector_ids: list[str]) -> None:
        if not self.client:
            raise RuntimeError("Milvus client not initialized")

        # Create filter for deleting specific IDs
        ids_str = ", ".join([f"'{vid}'" for vid in vector_ids])
        self.client.delete(
            collection_name=self.collection_name,
            filter=f"id in [{ids_str}]"
        )
