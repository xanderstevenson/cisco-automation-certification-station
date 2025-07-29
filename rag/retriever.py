import faiss
import pickle
from sentence_transformers import SentenceTransformer
import gc
import os

_model = None
_index = None
_texts = None

INDEX_PATH = "rag/index/faiss.index"
TEXTS_PATH = "rag/index/texts.pkl"

# Use smaller model for memory-constrained environments
MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

def _load_resources():
    global _model, _index, _texts
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    if _index is None:
        _index = faiss.read_index(INDEX_PATH)
    if _texts is None:
        with open(TEXTS_PATH, "rb") as f:
            _texts = pickle.load(f)

def cleanup_memory():
    """Force cleanup of unused memory"""
    global _model, _index, _texts
    gc.collect()

def retrieve_answer(query, k=3):
    _load_resources()
    query_vec = _model.encode([query])
    D, I = _index.search(query_vec, k)
    results = []
    for idx in I[0]:
        if idx < len(_texts):
            results.append(_texts[idx])
    return "\n---\n".join(results)
