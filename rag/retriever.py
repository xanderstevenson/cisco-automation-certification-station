import faiss
import pickle
from sentence_transformers import SentenceTransformer

_model = None
_index = None
_texts = None

INDEX_PATH = "rag/index/faiss.index"
TEXTS_PATH = "rag/index/texts.pkl"

def _load_resources():
    global _model, _index, _texts
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    if _index is None:
        _index = faiss.read_index(INDEX_PATH)
    if _texts is None:
        with open(TEXTS_PATH, "rb") as f:
            _texts = pickle.load(f)

def retrieve_answer(query, k=3):
    _load_resources()
    query_vec = _model.encode([query])
    D, I = _index.search(query_vec, k)
    results = []
    for idx in I[0]:
        if idx < len(_texts):
            results.append(_texts[idx])
    return "\n---\n".join(results)
