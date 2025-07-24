import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import textwrap

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 50  # characters

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def embed_documents(documents):
    # Flatten and chunk each document
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc)
        all_chunks.extend(chunks)
    print(f"[✓] Total chunks to embed: {len(all_chunks)}")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    return embeddings, all_chunks

def build_vector_store(documents, save_path="rag/index"):
    embeddings, all_chunks = embed_documents(documents)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(index, f"{save_path}/faiss.index")
    with open(f"{save_path}/texts.pkl", "wb") as f:
        pickle.dump(all_chunks, f)
