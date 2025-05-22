"""
Simple test script for document processing.
"""
import os
from src.utils.document_processor import DocumentProcessor

def main():
    """Run a simple test."""
    print("Starting simple document processing test...")

    # Create document processor
    processor = DocumentProcessor()

    # Test text processing
    test_text = "This is a test document for processing. It contains medical information about diabetes."
    with open("test_document.txt", "w") as f:
        f.write(test_text)

    try:
        # Process the test document
        chunks = processor.process_file("test_document.txt")
        print(f"Successfully processed text document into {len(chunks)} chunks")

        # Print the first chunk
        if chunks:
            print("First chunk content:", chunks[0]["content"])
            print("First chunk metadata:", chunks[0]["metadata"])

        # Clean up
        os.remove("test_document.txt")
    except Exception as e:
        print(f"Error processing text document: {e}")

    print("Test completed.")

if __name__ == "__main__":
    main()
