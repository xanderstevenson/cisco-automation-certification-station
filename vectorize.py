import os
from PyPDF2 import PdfReader
from rag.vector_store import build_vector_store

DOCS_DIR = "docs"

def load_text_from_pdfs(doc_dir):
    documents = []
    for filename in os.listdir(doc_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(doc_dir, filename)
            try:
                reader = PdfReader(pdf_path)
                text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                documents.append(text)
                print(f"[✓] Loaded: {filename}")
            except Exception as e:
                print(f"[!] Error reading {filename}: {e}")
    return documents

if __name__ == "__main__":
    print("📄 Loading and embedding Cisco PDFs...")
    texts = load_text_from_pdfs(DOCS_DIR)
    if texts:
        build_vector_store(texts)
        print("✅ Vector store built and saved to rag/index/")
    else:
        print("⚠️ No valid text found in PDFs.")
