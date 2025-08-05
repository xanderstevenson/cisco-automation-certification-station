import os
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import faiss
import pickle
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
URLS_FILE = "urls.txt"

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "footer", "nav", "header", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def load_text_from_pdfs(doc_dir):
    documents = []
    for filename in os.listdir(doc_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(doc_dir, filename)
            try:
                reader = PdfReader(pdf_path)
                text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                documents.append(text)
                print(f"[✓] Loaded PDF: {filename}")
            except Exception as e:
                print(f"[!] Error reading {filename}: {e}")
    return documents

def load_text_from_urls(urls_file):
    if not os.path.exists(urls_file):
        return []

    documents = []
    with open(urls_file, "r") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            try:
                response = requests.get(url, timeout=10)
                text = clean_html(response.text)
                documents.append(text)
                print(f"[✓] Loaded URL: {url}")
            except Exception as e:
                print(f"[!] Error fetching {url}: {e}")
    return documents

def build_vector_store(texts, model_name="paraphrase-MiniLM-L3-v2", chunk_size=500, chunk_overlap=50):
    """Build FAISS vector store from text documents"""
    print(f"🔧 Building vector store with {len(texts)} documents...")
    
    # Initialize sentence transformer
    model = SentenceTransformer(model_name)
    
    # Chunk the texts
    chunks = []
    for text in texts:
        # Simple chunking strategy
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk.strip()) > 20:  # Only keep meaningful chunks
                chunks.append(chunk.strip())
    
    print(f"📝 Created {len(chunks)} text chunks")
    
    # Create embeddings
    print("🔄 Generating embeddings...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Create output directory
    os.makedirs("rag/index", exist_ok=True)
    
    # Save FAISS index and texts
    faiss.write_index(index, "rag/index/faiss.index")
    with open("rag/index/texts.pkl", "wb") as f:
        pickle.dump(chunks, f)
    
    print(f"💾 Saved vector store: {len(chunks)} chunks, {dimension}D embeddings")
    return index, chunks

def vectorize_all():
    print("📄 Loading documents (PDFs + URLs)...")
    pdf_texts = load_text_from_pdfs(DOCS_DIR)
    url_texts = load_text_from_urls(URLS_FILE)
    all_texts = pdf_texts + url_texts

    if all_texts:
        build_vector_store(all_texts)
        print("✅ Vector store built and saved to rag/index/")
        return True
    else:
        print("⚠️ No valid content found to embed.")
        return False

if __name__ == "__main__":
    vectorize_all()
