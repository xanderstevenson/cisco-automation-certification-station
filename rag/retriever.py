import faiss
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("rag/index/faiss.index")
with open("rag/index/texts.pkl", "rb") as f:
    texts = pickle.load(f)

def retrieve_answer(query, k=3):
    query_vec = model.encode([query])
    D, I = index.search(query_vec, k)
    return "\n---\n".join([texts[i] for i in I[0]])
