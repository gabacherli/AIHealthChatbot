"""
Vector database service.
This module contains functions for interacting with the Qdrant vector database.
"""
import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from ..config.base import BaseConfig

config = BaseConfig()

class VectorDBService:
    """Service for interacting with the Qdrant vector database."""

    def __init__(self):
        """Initialize the vector database service."""
        self.collection_name = getattr(config, 'VECTOR_DB_COLLECTION', 'health_documents')
        self.vector_size = getattr(config, 'VECTOR_SIZE', 768)
        self.client = None

        try:
            # Initialize Qdrant client
            self._init_client()

            # Ensure collection exists
            if self.client:
                self._ensure_collection()
        except Exception as e:
            print(f"Error initializing vector database: {e}")
            print("Vector database functionality will be limited")

    def _init_client(self):
        """Initialize the Qdrant client."""
        try:
            from qdrant_client import QdrantClient

            vector_db_url = getattr(config, 'VECTOR_DB_URL', '')
            vector_db_api_key = getattr(config, 'VECTOR_DB_API_KEY', '')
            vector_db_local_path = getattr(config, 'VECTOR_DB_LOCAL_PATH', './qdrant_data')

            if vector_db_url:
                # Connect to remote Qdrant instance
                self.client = QdrantClient(
                    url=vector_db_url,
                    api_key=vector_db_api_key
                )
                print(f"Connected to remote Qdrant instance at {vector_db_url}")
            else:
                # Use local Qdrant instance
                # Ensure the directory exists
                os.makedirs(vector_db_local_path, exist_ok=True)

                self.client = QdrantClient(
                    path=vector_db_local_path
                )
                print(f"Connected to local Qdrant instance at {vector_db_local_path}")
        except Exception as e:
            print(f"Failed to initialize Qdrant client: {e}")
            self.client = None

    def _ensure_collection(self):
        """Ensure the collection exists, create it if it doesn't."""
        if not self.client:
            return

        try:
            from qdrant_client.http import models

            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    ),
                    optimizers_config=models.OptimizersConfigDiff(
                        indexing_threshold=0  # Index immediately
                    )
                )
                print(f"Created collection '{self.collection_name}' in Qdrant")

                # Create payload indexes for efficient filtering
                self._create_payload_indexes()
            else:
                print(f"Collection '{self.collection_name}' already exists in Qdrant")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")

    def _create_payload_indexes(self):
        """Create payload indexes for efficient filtering."""
        if not self.client:
            return

        try:
            from qdrant_client.http import models

            # Index for source document filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.source",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            # Index for content type filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.content_type",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            # Index for user role filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.user_role",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            # Index for user ID filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.user_id",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

            print("Created payload indexes for efficient filtering")
        except Exception as e:
            print(f"Error creating payload indexes: {e}")

    def store_embeddings(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Store document chunks with embeddings in the vector database.

        Args:
            chunks: List of document chunks with content, metadata, and embeddings.

        Returns:
            List of IDs for the stored points.
        """
        if not self.client:
            print("Vector database client not initialized, cannot store embeddings")
            return []

        try:
            from qdrant_client.http.models import PointStruct

            points = []
            ids = []

            for chunk in chunks:
                if "embedding" not in chunk:
                    continue

                # Generate a unique ID
                point_id = str(uuid.uuid4())
                ids.append(point_id)

                # Create the point
                point = PointStruct(
                    id=point_id,
                    vector=chunk["embedding"].tolist(),
                    payload={
                        "content": chunk["content"],
                        "metadata": chunk["metadata"]
                    }
                )

                points.append(point)

            # Store points in batches
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                print(f"Stored {len(points)} embeddings in Qdrant")

            return ids
        except Exception as e:
            print(f"Error storing embeddings: {e}")
            return []

    def search_similar(
        self,
        query_vector: np.ndarray,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_vector: The query vector.
            limit: Maximum number of results to return.
            filters: Optional filters to apply to the search.

        Returns:
            List of similar documents with scores.
        """
        if not self.client:
            print("Vector database client not initialized, cannot search")
            return []

        try:
            from qdrant_client.http import models

            filter_query = None
            if filters:
                filter_conditions = []

                # Process source filter
                if "source" in filters and filters["source"]:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.source",
                            match=models.MatchValue(value=filters["source"])
                        )
                    )

                # Process content type filter
                if "content_type" in filters and filters["content_type"]:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.content_type",
                            match=models.MatchValue(value=filters["content_type"])
                        )
                    )

                # Process user role filter
                if "user_role" in filters and filters["user_role"]:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.user_role",
                            match=models.MatchValue(value=filters["user_role"])
                        )
                    )

                # Process user ID filter
                if "user_id" in filters and filters["user_id"]:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.user_id",
                            match=models.MatchValue(value=filters["user_id"])
                        )
                    )

                if filter_conditions:
                    filter_query = models.Filter(
                        must=filter_conditions
                    )

            # Perform the search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                filter=filter_query
            )

            # Format the results
            results = []
            for scored_point in search_result:
                results.append({
                    "id": scored_point.id,
                    "content": scored_point.payload["content"],
                    "metadata": scored_point.payload["metadata"],
                    "score": scored_point.score
                })

            return results
        except Exception as e:
            print(f"Error searching similar documents: {e}")
            return []

    def delete_by_source(self, source: str) -> int:
        """
        Delete all points associated with a source document.

        Args:
            source: The source document name.

        Returns:
            Number of points deleted.
        """
        if not self.client:
            print("Vector database client not initialized, cannot delete")
            return 0

        try:
            from qdrant_client.http import models

            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=source)
                    )
                ]
            )

            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=filter_query
                )
            )

            print(f"Deleted {result.deleted} points for source '{source}'")
            return result.deleted
        except Exception as e:
            print(f"Error deleting by source: {e}")
            return 0

    def delete_by_source_and_user(self, source: str, user_id: str) -> int:
        """
        Delete all points associated with a source document and user ID.

        Args:
            source: The source document name.
            user_id: The user ID.

        Returns:
            Number of points deleted.
        """
        if not self.client:
            print("Vector database client not initialized, cannot delete")
            return 0

        try:
            from qdrant_client.http import models

            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=source)
                    ),
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )

            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=filter_query
                )
            )

            print(f"Deleted {result.deleted} points for source '{source}' and user '{user_id}'")
            return result.deleted
        except Exception as e:
            print(f"Error deleting by source and user: {e}")
            return 0

    def get_all_sources(self) -> List[str]:
        """
        Get a list of all source documents in the database.

        Returns:
            List of source document names.
        """
        if not self.client:
            print("Vector database client not initialized, cannot get sources")
            return []

        try:
            # Use scroll to get all points efficiently
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                with_payload=["metadata.source"],
                with_vectors=False
            )

            sources = set()
            points = scroll_result[0]

            while points:
                for point in points:
                    if "metadata" in point.payload and "source" in point.payload["metadata"]:
                        sources.add(point.payload["metadata"]["source"])

                # Get next batch
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    with_payload=["metadata.source"],
                    with_vectors=False,
                    offset=scroll_result[1]
                )
                points = scroll_result[0]

            return list(sources)
        except Exception as e:
            print(f"Error getting all sources: {e}")
            return []
