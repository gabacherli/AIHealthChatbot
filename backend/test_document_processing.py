"""
Test script for document processing and retrieval.
"""
import os
import sys
from src.utils.document_processor import DocumentProcessor
from src.services.medical_embedding_service import MedicalEmbeddingService
from src.services.vector_db_service import VectorDBService
from src.services.document_service import DocumentService

def test_document_processor():
    """Test the document processor."""
    print("Testing document processor...")
    
    # Create document processor
    processor = DocumentProcessor()
    
    # Test text processing
    test_text = "This is a test document for processing. It contains medical information about diabetes."
    with open("test_document.txt", "w") as f:
        f.write(test_text)
    
    try:
        # Process the test document
        chunks = processor.process_file("test_document.txt", "test_document.txt")
        print(f"Successfully processed text document into {len(chunks)} chunks")
        
        # Print the first chunk
        if chunks:
            print("First chunk content:", chunks[0]["content"])
            print("First chunk metadata:", chunks[0]["metadata"])
        
        # Clean up
        os.remove("test_document.txt")
    except Exception as e:
        print(f"Error processing text document: {e}")

def test_embedding_service():
    """Test the embedding service."""
    print("\nTesting embedding service...")
    
    # Create embedding service
    embedding_service = MedicalEmbeddingService()
    
    # Test text embedding
    test_text = "Diabetes is a chronic condition that affects how your body turns food into energy."
    try:
        embedding = embedding_service.get_text_embedding(test_text)
        print(f"Successfully generated text embedding with shape: {embedding.shape}")
    except Exception as e:
        print(f"Error generating text embedding: {e}")

def test_vector_db_service():
    """Test the vector database service."""
    print("\nTesting vector database service...")
    
    # Create vector database service
    vector_db_service = VectorDBService()
    
    # Test connection
    try:
        if vector_db_service.client:
            print("Successfully connected to vector database")
        else:
            print("Failed to connect to vector database")
    except Exception as e:
        print(f"Error connecting to vector database: {e}")

def test_document_service():
    """Test the document service."""
    print("\nTesting document service...")
    
    # Create document service
    document_service = DocumentService()
    
    # Test search
    test_query = "What are the symptoms of diabetes?"
    try:
        results = document_service.search_documents(test_query)
        print(f"Successfully searched for documents with query: '{test_query}'")
        print(f"Found {len(results)} results")
    except Exception as e:
        print(f"Error searching for documents: {e}")

def main():
    """Run all tests."""
    print("Starting document processing and retrieval tests...\n")
    
    test_document_processor()
    test_embedding_service()
    test_vector_db_service()
    test_document_service()
    
    print("\nTests completed.")

if __name__ == "__main__":
    main()
