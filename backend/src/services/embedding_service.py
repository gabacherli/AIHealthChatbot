import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..utils.document_loader import load_and_chunk_documents
from ..config.config import Config

config = Config()
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
    if model is None or index is None:
        # Model or index is not initialized
        return

    q_vec = model.encode([query])
    D, I = index.search(np.array(q_vec, dtype='float32'), top_k)
    return "\n".join([doc_texts[i] for i in I[0] if i != -1])
