"""
Document loader utility.
This module contains functions for loading and chunking documents.
"""
import os

def load_and_chunk_documents(folder_path, chunk_size=1000):
    """
    Load and chunk documents from a folder.

    Args:
        folder_path: The path to the folder containing the documents.
        chunk_size: The size of each chunk in characters.

    Returns:
        A list of document chunks.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    docs = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    # Simple chunking: split every chunk_size characters
                    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                    docs.extend(chunks)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")

    return docs
