"""
Embedding service.
This module contains functions for embedding and retrieving context.
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..utils.document_loader import load_and_chunk_documents
from ..config import get_config

config = get_config()

docs = load_and_chunk_documents(config.CHUNK_DATA_PATH)

model = None
index = None
doc_texts = []

if docs:
    model = SentenceTransformer(config.EMBEDDING_MODEL)
    doc_embeddings = np.array(model.encode(docs), dtype='float32')

    index = faiss.IndexFlatL2(doc_embeddings.shape[1])
    index.add(doc_embeddings)
    doc_texts = docs

def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve context for a query.

    Args:
        query: The query to retrieve context for.
        top_k: The number of top results to return.

    Returns:
        A string containing the context for the query.
    """
    if model is None or index is None:
        return ""

    q_vec = model.encode([query])

    # Search for similar documents
    D, I = index.search(np.array(q_vec, dtype='float32'), top_k)

    # Join the results
    return "\n".join([doc_texts[i] for i in I[0] if i != -1])
