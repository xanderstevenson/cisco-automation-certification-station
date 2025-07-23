# Cisco Automation Certification Station 🤖

A RAG-based chatbot for Cisco certification topics using Chainlit, Hugging Face models, and FAISS.

## Features
- 🧠 RAG pipeline using sentence-transformers
- 📚 Embed Cisco docs for context retrieval
- 💬 Chat interface via Chainlit
- 🚀 Deploy to Render with `render.yaml`

## Quick Start

1. Add your Cisco PDFs/markdowns into the `docs/` folder
2. Embed them with `vector_store.py`
3. Run Chainlit:
   ```bash
   chainlit run app.py
   ```


