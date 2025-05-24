"""
Vector database service.
This module contains functions for interacting with the Qdrant vector database.
"""
import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from ..config.base import BaseConfig

config = BaseConfig()

class VectorDBService:
    """Service for interacting with the Qdrant vector database."""

    _instance = None
    _initialized = False
    _lock = None

    def __new__(cls):
        """Implement singleton pattern to prevent multiple Qdrant instances."""
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()

            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VectorDBService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the vector database service."""
        # Only initialize once per process
        if VectorDBService._initialized:
            return

        self.collection_name = getattr(config, 'VECTOR_DB_COLLECTION', 'health_documents')
        self.vector_size = getattr(config, 'VECTOR_SIZE', 768)
        self.client = None

        try:
            # Initialize Qdrant client
            self._init_client()

            # Ensure collection exists
            if self.client:
                self._ensure_collection()

            VectorDBService._initialized = True
        except Exception as e:
            logger.exception("Failed to initialize VectorDBService: %s", e)

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
            else:
                # Use local Qdrant instance
                # Ensure the directory exists
                os.makedirs(vector_db_local_path, exist_ok=True)

                # Try to connect with timeout and retry logic
                import time
                max_retries = 3
                retry_delay = 2

                for attempt in range(max_retries):
                    try:
                        self.client = QdrantClient(
                            path=vector_db_local_path,
                            timeout=30  # Add timeout
                        )
                        break
                    except Exception as retry_error:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            raise retry_error

        except Exception:
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

                # Create payload indexes for efficient filtering
                self._create_payload_indexes()
        except Exception:
            pass

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

        except Exception:
            pass

    def store_embeddings(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Store document chunks with embeddings in the vector database.

        Args:
            chunks: List of document chunks with content, metadata, and embeddings.

        Returns:
            List of IDs for the stored points.
        """
        if not self.client:
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

                # Prepare metadata for storage (handle binary data properly)
                storage_metadata = chunk["metadata"].copy()

                # Handle image data properly for medical compliance
                if "image_data" in storage_metadata:
                    # For medical images, we need to preserve the data but handle JSON serialization
                    # Option 1: Store file path reference (images are already saved to disk)
                    # Option 2: Use base64 encoding for smaller images
                    # Option 3: Store in separate blob storage

                    image_data = storage_metadata.pop("image_data")
                    image_size = len(image_data)

                    if image_size < 1024 * 1024:  # Less than 1MB - use base64 encoding
                        import base64
                        storage_metadata["image_data_base64"] = base64.b64encode(image_data).decode('utf-8')
                        storage_metadata["image_storage_method"] = "base64_embedded"
                    else:
                        # For larger images, rely on file system storage
                        storage_metadata["image_storage_method"] = "file_system"
                        storage_metadata["image_file_size"] = image_size

                    storage_metadata["has_image_data"] = True

                # Create the point
                point = PointStruct(
                    id=point_id,
                    vector=chunk["embedding"].tolist(),
                    payload={
                        "content": chunk["content"],
                        "metadata": storage_metadata
                    }
                )

                points.append(point)

            # Store points in batches
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

            return ids
        except Exception:
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

            # Handle different Qdrant response formats
            deleted_count = 0
            if hasattr(result, 'deleted'):
                deleted_count = result.deleted
            elif hasattr(result, 'operation_id'):
                # For async operations, assume success if no error
                deleted_count = 1
            else:
                # If we can't determine count, assume success if no exception
                deleted_count = 1

            print(f"Deleted {deleted_count} points for source '{source}'")
            return deleted_count
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

            # Handle different Qdrant response formats
            deleted_count = 0
            if hasattr(result, 'deleted'):
                deleted_count = result.deleted
            elif hasattr(result, 'operation_id'):
                # For async operations, assume success if no error
                deleted_count = 1
            else:
                # If we can't determine count, assume success if no exception
                deleted_count = 1

            print(f"Deleted {deleted_count} points for source '{source}' and user '{user_id}'")
            return deleted_count
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
