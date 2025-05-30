"""
Document service.
This module contains functions for document processing and management.
"""
import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from ..utils.document_processor import DocumentProcessor
from .medical_embedding_service import MedicalEmbeddingService
from .vector_db_service import VectorDBService
from ..config import get_config

logger = logging.getLogger(__name__)
config = get_config()

class DocumentService:
    """Service for document processing and management."""

    _instance = None
    _initialized = False
    _lock = None

    def __new__(cls):
        """Implement singleton pattern to prevent multiple DocumentService instances."""
        if cls._instance is None:
            import threading
            if cls._lock is None:
                cls._lock = threading.Lock()

            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DocumentService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the document service."""
        # Only initialize once per process
        if DocumentService._initialized:
            return

        logger.info("Initializing DocumentService singleton...")

        try:
            self.document_processor = DocumentProcessor(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )
            self.embedding_service = MedicalEmbeddingService()
            self.vector_db_service = VectorDBService()

            DocumentService._initialized = True
            logger.info("DocumentService singleton initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DocumentService: {e}")
            raise

    def process_and_store_document(
        self,
        file_path: str,
        filename: str,
        user_role: str = "patient",
        user_id: str = None
    ) -> str:
        """
        Process and store a document.

        Args:
            file_path: The path to the document file.
            filename: The name of the file.
            user_role: The role of the user who uploaded the document.
            user_id: The ID of the user who uploaded the document.

        Returns:
            The ID of the processed document.
        """
        # Process the document into chunks
        chunks = self.document_processor.process_file(file_path)

        # Add user role and user ID to metadata
        for chunk in chunks:
            chunk["metadata"]["user_role"] = user_role
            chunk["metadata"]["source"] = filename
            if user_id:
                chunk["metadata"]["user_id"] = user_id

        # Generate embeddings for the chunks
        chunks_with_embeddings = self.embedding_service.embed_document_chunks(chunks)

        # Store the chunks in the vector database
        chunk_ids = self.vector_db_service.store_embeddings(chunks_with_embeddings)

        # Return a document ID (using the first chunk ID)
        return chunk_ids[0] if chunk_ids else str(uuid.uuid4())

    def process_and_store_document_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        user_role: str = "patient",
        user_id: str = None
    ) -> str:
        """
        Process and store a document from bytes.

        Args:
            file_bytes: The document file as bytes.
            filename: The name of the file.
            user_role: The role of the user who uploaded the document.
            user_id: The ID of the user who uploaded the document.

        Returns:
            The ID of the processed document.
        """
        # Process the document into chunks
        chunks = self.document_processor.process_bytes(file_bytes, filename)

        # Add user role and user ID to metadata
        for chunk in chunks:
            chunk["metadata"]["user_role"] = user_role
            chunk["metadata"]["source"] = filename
            if user_id:
                chunk["metadata"]["user_id"] = user_id

        # Generate embeddings for the chunks
        chunks_with_embeddings = self.embedding_service.embed_document_chunks(chunks)

        # Store the chunks in the vector database
        chunk_ids = self.vector_db_service.store_embeddings(chunks_with_embeddings)

        # Return a document ID (using the first chunk ID)
        return chunk_ids[0] if chunk_ids else str(uuid.uuid4())

    def list_documents(self) -> List[str]:
        """
        List all documents.

        Returns:
            A list of document names.
        """
        return self.vector_db_service.get_all_sources()



    def get_document_metadata(self, document_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific document.

        Args:
            document_id: The ID of the document

        Returns:
            Document metadata dictionary or None
        """
        try:
            # Get document from vector database by ID
            points = self.vector_db_service.client.retrieve(
                collection_name=self.vector_db_service.collection_name,
                ids=[document_id]
            )

            if points and len(points) > 0:
                point = points[0]
                metadata = point.payload.get("metadata", {})

                # Base metadata
                result = {
                    "id": point.id,
                    "source": metadata.get("source"),
                    "content_type": metadata.get("content_type", "unknown"),
                    "user_id": metadata.get("user_id"),
                    "user_role": metadata.get("user_role"),
                    "upload_date": metadata.get("upload_date"),
                    "filename": metadata.get("source")
                }

                # Add medical keywords if available
                if metadata.get("medical_keywords"):
                    result["medical_keywords"] = metadata.get("medical_keywords")
                    result["keywords_count"] = metadata.get("keywords_count", 0)

                # Add medical context information
                if metadata.get("medical_context"):
                    result["medical_context"] = True
                    result["medical_type"] = metadata.get("medical_type")
                    result["is_dicom"] = metadata.get("is_dicom", False)

                return result

            return None

        except Exception as e:
            return None

    def get_documents_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of documents with metadata.
        """
        if not self.vector_db_service.client:
            return []

        try:
            from qdrant_client.http import models

            # Convert user_id to integer if it's a numeric string
            # Documents are stored with integer user_ids
            query_user_id = user_id
            if isinstance(user_id, str) and user_id.isdigit():
                query_user_id = int(user_id)
            elif isinstance(user_id, str):
                # If it's not a digit, try to handle it as is (for backward compatibility)
                query_user_id = user_id

            # Create proper filter using Qdrant models
            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=query_user_id)
                    )
                ]
            )

            # Use scroll to get all points efficiently
            scroll_result = self.vector_db_service.client.scroll(
                collection_name=self.vector_db_service.collection_name,
                limit=100,
                with_payload=["metadata"],
                with_vectors=False,
                scroll_filter=filter_query
            )

            documents = {}
            points = scroll_result[0]
            next_page_offset = scroll_result[1]
            max_iterations = 10  # Safety limit to prevent infinite loops

            iteration = 0
            while points and iteration < max_iterations:
                iteration += 1

                for i, point in enumerate(points):
                    if "metadata" in point.payload and "source" in point.payload["metadata"]:
                        source = point.payload["metadata"]["source"]
                        if source not in documents:
                            # Prepare metadata for document listing
                            metadata = {
                                k: v for k, v in point.payload["metadata"].items()
                                if k not in ["chunk", "total_chunks", "page", "image_data_base64", "image_data"]
                            }

                            # Add image retrieval information for medical images
                            if point.payload["metadata"].get("content_type") == "image":
                                metadata["is_medical_image"] = True
                                metadata["image_available"] = True

                                # Indicate how the image can be retrieved
                                storage_method = point.payload["metadata"].get("image_storage_method", "file_system")
                                metadata["image_storage_method"] = storage_method

                                if storage_method == "base64_embedded":
                                    metadata["image_embedded"] = True
                                elif storage_method == "file_system":
                                    metadata["image_file_available"] = True

                                # Include medical keywords and context for medical images
                                if point.payload["metadata"].get("medical_keywords"):
                                    metadata["medical_keywords"] = point.payload["metadata"]["medical_keywords"]
                                    metadata["keywords_count"] = point.payload["metadata"].get("keywords_count", 0)

                                if point.payload["metadata"].get("medical_context"):
                                    metadata["medical_context"] = True
                                    metadata["medical_type"] = point.payload["metadata"].get("medical_type")
                                    metadata["is_dicom"] = point.payload["metadata"].get("is_dicom", False)

                            documents[source] = {
                                "filename": source,
                                "id": point.id,
                                "metadata": metadata
                            }

                # Check if there are more points to fetch
                if next_page_offset is None:
                    break

                # Get next batch
                try:
                    scroll_result = self.vector_db_service.client.scroll(
                        collection_name=self.vector_db_service.collection_name,
                        limit=100,
                        with_payload=["metadata"],
                        with_vectors=False,
                        offset=next_page_offset,
                        scroll_filter=filter_query
                    )
                    points = scroll_result[0]
                    next_page_offset = scroll_result[1]

                    # If no new points, break
                    if not points:
                        break

                except Exception:
                    break

            return list(documents.values())
        except Exception as e:
            return []

    def delete_document(self, filename: str, user_id: Optional[str] = None) -> int:
        """
        Delete a document.

        Args:
            filename: The name of the file to delete.
            user_id: Optional user ID for authorization.

        Returns:
            The number of chunks deleted, or 1 if file was deleted successfully.
        """
        # Check if document exists before deletion
        if user_id:
            file_path = os.path.join(config.UPLOAD_FOLDER, user_id, filename)
        else:
            file_path = os.path.join(config.UPLOAD_FOLDER, filename)

        file_existed = os.path.exists(file_path)

        # Delete the document from the vector database
        num_deleted = 0
        if user_id:
            # Delete only documents owned by the user
            num_deleted = self.vector_db_service.delete_by_source_and_user(filename, user_id)
        else:
            # Delete all documents with the given filename
            num_deleted = self.vector_db_service.delete_by_source(filename)

        # Delete the file if it exists
        file_deleted = False
        if file_existed:
            try:
                os.remove(file_path)
                file_deleted = True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to delete file from disk: {file_path}, error: {e}")
                file_deleted = False

        # Return success if either vector DB deletion worked or file was deleted
        # This handles cases where Qdrant might not report deletions correctly
        total_deleted = max(num_deleted, 1 if file_deleted else 0)

        return total_deleted

    def get_medical_image_data(self, filename: str, user_id: str) -> Optional[bytes]:
        """
        Retrieve medical image data for a specific file.

        Args:
            filename: The name of the image file.
            user_id: The ID of the user who owns the image.

        Returns:
            The image data as bytes, or None if not found.
        """
        try:
            from qdrant_client.http import models

            # Convert user_id to integer if it's a numeric string
            query_user_id = user_id
            if isinstance(user_id, str) and user_id.isdigit():
                query_user_id = int(user_id)

            # Search for the specific image document
            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=query_user_id)
                    ),
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=filename)
                    ),
                    models.FieldCondition(
                        key="metadata.content_type",
                        match=models.MatchValue(value="image")
                    )
                ]
            )

            # Search for the image document
            scroll_result = self.vector_db_service.client.scroll(
                collection_name=self.vector_db_service.collection_name,
                limit=1,
                with_payload=True,
                with_vectors=False,
                scroll_filter=filter_query
            )

            points = scroll_result[0]
            if not points:
                return None

            point = points[0]
            metadata = point.payload.get("metadata", {})
            storage_method = metadata.get("image_storage_method", "file_system")

            if storage_method == "base64_embedded":
                # Retrieve from base64 encoded data
                image_data_base64 = metadata.get("image_data_base64")
                if image_data_base64:
                    import base64
                    return base64.b64decode(image_data_base64)
                else:
                    return None

            elif storage_method == "file_system":
                # Retrieve from file system
                from ..config import get_config
                config = get_config()

                import os
                file_path = os.path.join(config.UPLOAD_FOLDER, user_id, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
                else:
                    return None

            else:
                return None

        except Exception:
            return None

    def search_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents.

        Args:
            query: The search query.
            filters: Optional filters to apply to the search.

        Returns:
            A list of search results.
        """
        # Generate embedding for the query
        query_embedding = self.embedding_service.get_text_embedding(query)

        # Search for similar documents
        results = self.vector_db_service.search_similar(
            query_embedding,
            limit=5,
            filters=filters
        )

        # FALLBACK: If vector search returns no results, try a direct scroll-based search
        if len(results) == 0 and filters:
            results = self._fallback_scroll_search(filters, limit=5)

        return results

    def _fallback_scroll_search(self, filters: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback search using scroll when vector search fails.

        Args:
            filters: Filters to apply
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        try:
            from qdrant_client.http import models

            # Build filter conditions
            filter_conditions = []

            if "user_id" in filters and filters["user_id"]:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=filters["user_id"])
                    )
                )

            if "source" in filters and filters["source"]:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=filters["source"])
                    )
                )

            filter_query = None
            if filter_conditions:
                filter_query = models.Filter(must=filter_conditions)

            # Use scroll to get matching documents
            scroll_result = self.vector_db_service.client.scroll(
                collection_name=self.vector_db_service.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                scroll_filter=filter_query
            )

            points = scroll_result[0]

            # Format results to match vector search format
            results = []
            for point in points:
                # Prepare metadata, excluding large binary data
                metadata = {
                    k: v for k, v in point.payload["metadata"].items()
                    if k not in ["image_data", "image_data_base64"]
                }

                results.append({
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "metadata": metadata,
                    "score": 1.0  # Default score for scroll-based results
                })

            return results

        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return []

    def retrieve_context_for_query(
        self,
        query: str,
        user_role: str = "patient",
        top_k: int = 3
    ) -> str:
        """
        Retrieve context for a query.

        Args:
            query: The query to retrieve context for.
            user_role: The role of the user making the query.
            top_k: The number of top results to return.

        Returns:
            A string containing the context for the query.
        """
        # Generate embedding for the query
        query_embedding = self.embedding_service.get_text_embedding(query)

        # Search for similar documents
        results = self.vector_db_service.search_similar(
            query_embedding,
            limit=top_k,
            filters={"user_role": user_role}
        )

        # Format the results as context
        context_parts = []
        for i, result in enumerate(results):
            source = result["metadata"].get("source", "Unknown")
            page = result["metadata"].get("page", "")
            page_info = f" (Page {page})" if page else ""

            context_parts.append(f"[Document {i+1}: {source}{page_info}]\n{result['content']}\n")

        return "\n".join(context_parts)


# Create a singleton instance for easy import
document_service = DocumentService()
