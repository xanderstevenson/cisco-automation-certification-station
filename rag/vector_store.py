import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_documents(documents):
    return model.encode(documents)

def build_vector_store(texts, save_path="rag/index"):
    embeddings = embed_documents(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(index, f"{save_path}/faiss.index")
    with open(f"{save_path}/texts.pkl", "wb") as f:
        pickle.dump(texts, f)
