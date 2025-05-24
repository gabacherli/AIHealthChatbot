"""
Document service.
This module contains functions for document processing and management.
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from ..utils.document_processor import DocumentProcessor
from .medical_embedding_service import MedicalEmbeddingService
from .vector_db_service import VectorDBService
from ..config import get_config

config = get_config()

class DocumentService:
    """Service for document processing and management."""

    def __init__(self):
        """Initialize the document service."""
        self.document_processor = DocumentProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.embedding_service = MedicalEmbeddingService()
        self.vector_db_service = VectorDBService()

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

    def get_documents_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of documents with metadata.
        """
        if not self.vector_db_service.client:
            print("Vector database client not available, returning empty list")
            return []

        try:
            from qdrant_client.http import models

            # Create proper filter using Qdrant models
            filter_query = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id)
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
                print(f"Processing batch {iteration} with {len(points)} points")

                for point in points:
                    if "metadata" in point.payload and "source" in point.payload["metadata"]:
                        source = point.payload["metadata"]["source"]
                        if source not in documents:
                            documents[source] = {
                                "filename": source,
                                "id": point.id,
                                "metadata": {
                                    k: v for k, v in point.payload["metadata"].items()
                                    if k not in ["chunk", "total_chunks", "page"]
                                }
                            }

                # Check if there are more points to fetch
                if next_page_offset is None:
                    print("No more pages to fetch")
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
                        print("No more points returned")
                        break

                except Exception as scroll_error:
                    print(f"Error in scroll pagination: {scroll_error}")
                    break

            return list(documents.values())
        except Exception as e:
            print(f"Error getting documents by user: {e}")
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
                print(f"Successfully deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        # Return success if either vector DB deletion worked or file was deleted
        # This handles cases where Qdrant might not report deletions correctly
        if num_deleted > 0 or file_deleted:
            return max(num_deleted, 1)  # Return at least 1 if file was deleted

        return 0

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

        return results

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
