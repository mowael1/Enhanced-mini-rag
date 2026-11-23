
import logging
from uuid import uuid4

from qdrant_client import models, QdrantClient

from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
# from models.db_schemes import RetrieveDocument
from helpers.config import get_settings


class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        self.db_path = db_path
        self.client = None
        self.logger = logging.getLogger(__name__)

        distance_map = {
            DistanceMethodEnums.COSINE.value: models.Distance.COSINE,
            DistanceMethodEnums.DOT.value: models.Distance.DOT,
        }

        if distance_method not in distance_map:
            raise ValueError(
                f"Unsupported distance method: {distance_method}"
            )

        self.distance_method = distance_map[distance_method]

        self.settings = get_settings()
        self.limit_documents = self.settings.limit_documents

    def _get_client(self) -> QdrantClient:
        if self.client is None:
            raise RuntimeError("Qdrant is not connected. Call connect() first.")

        return self.client

    def connect(self):
        if self.client is None:
            self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        if self.client is not None:
            try:
                self.client.close()
            finally:
                self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self._get_client().collection_exists(
            collection_name=collection_name
        )

    def list_all_collection(self) -> list[str]:
        response = self._get_client().get_collections()
        return [collection.name for collection in response.collections]

    def get_collection_info(self, collection_name: str) -> dict:
        response = self._get_client().get_collection(
            collection_name=collection_name
        )
        return response.model_dump()

    def delete_collection(self, collection_name: str) -> bool:

        if not self.is_collection_existed(collection_name):
            self.logger.warning(
                f"Collection {collection_name} does not exist"
            )
            return False

        return self._get_client().delete_collection(
            collection_name=collection_name
        )

    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:

        if embedding_size <= 0:
            raise ValueError("embedding_size must be positive")

        if do_reset:
            self.delete_collection(collection_name)

        if self.is_collection_existed(collection_name):
            return False

        return self._get_client().create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=self.distance_method,
            )
        )

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list[float],
        metadata: dict = None,
        record_id: str | int = None
    ) -> bool:

        if not self.is_collection_existed(collection_name):
            self.logger.warning(
                f"Collection {collection_name} does not exist"
            )
            return False

        point_id = record_id if record_id is not None else str(uuid4())

        payload = {
            **(metadata or {}),
            "text": text
        }

        try:
            self._get_client().upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ],
                wait=True
            )

            return True

        except Exception:
            self.logger.exception("Error inserting record")
            return False

    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list[list[float]],
        metadata: list[dict] = None,
        record_ids: list = None,
        batch_size: int = 50
    ) -> bool:

        if not self.is_collection_existed(collection_name):
            self.logger.warning(
                f"Collection {collection_name} does not exist"
            )
            return False

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        n = len(texts)

        if metadata is None:
            metadata = [{} for _ in range(n)]

        if record_ids is None:
            record_ids = [str(uuid4()) for _ in range(n)]
        else:
            record_ids = [
                rid if rid is not None else str(uuid4())
                for rid in record_ids
            ]

        if not (
            len(vectors) == len(metadata) == len(record_ids) == n
        ):
            raise ValueError(
                "texts, vectors, metadata and record_ids "
                "must have the same length"
            )

        try:
            points = []

            for text, vector, meta, record_id in zip(
                texts, vectors, metadata, record_ids
            ):
                points.append(
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            **(meta or {}),
                            "text": text
                        }
                    )
                )

            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]

                self._get_client().upsert(
                    collection_name=collection_name,
                    points=batch,
                    wait=True
                )

            return True

        except Exception:
            self.logger.exception("Error inserting batch")
            return False

    def search_by_vector(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 5
    ) -> list[RetrieveDocument]:

        if not self.is_collection_existed(collection_name):
            self.logger.warning(
                f"Collection {collection_name} does not exist"
            )
            return []

        search_limit = (
            self.limit_documents if limit is None else limit
        )

        if search_limit <= 0:
            raise ValueError("Search limit must be positive")

        results = self._get_client().query_points(
            collection_name=collection_name,
            query=vector,
            limit=search_limit,
            with_payload=True
        )

        return [
            RetrieveDocument(
                text=result.payload["text"],
                score=result.score
            )
            for result in results.points
        ]
