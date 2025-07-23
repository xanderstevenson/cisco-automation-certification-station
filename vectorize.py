import os
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from rag.vector_store import build_vector_store

DOCS_DIR = "docs"
URLS_FILE = "urls.txt"

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
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                documents.append(text)
                print(f"[✓] Loaded URL: {url}")
            except Exception as e:
                print(f"[!] Error fetching {url}: {e}")
    return documents

if __name__ == "__main__":
    print("📄 Loading documents (PDFs + URLs)...")
    pdf_texts = load_text_from_pdfs(DOCS_DIR)
    url_texts = load_text_from_urls(URLS_FILE)
    all_texts = pdf_texts + url_texts

    if all_texts:
        build_vector_store(all_texts)
        print("✅ Vector store built and saved to rag/index/")
    else:
        print("⚠️ No valid content found to embed.")
