# Cisco Automation Certification Station 🤖

A sophisticated **Hybrid RAG-powered AI assistant** for Cisco network automation certification preparation. This system combines local document search with web search and Google Gemini AI to provide comprehensive, source-backed answers for CCNA Auto, ENAUTO, DCNAUTO, AUTOCOR, and CCIE Automation topics.

## 🌟 Features

### **Hybrid RAG Architecture**
- 🔍 **Local Document Search**: FAISS vector store with 10 official Cisco certification PDFs
- 🌐 **Web Search Integration**: Real-time information via SerpAPI
- 🤖 **Google Gemini AI**: Free, high-quality response generation
- 💬 **Dual Interfaces**: Command-line and beautiful Chainlit web UI

### **Smart Conversation Handling**
- 🎯 **Intelligent Routing**: Casual greetings vs. technical questions
- 📚 **Official Cisco Focus**: Prioritizes Cisco U, Learning Network, NetAcad
- 🔗 **Clickable URLs**: Provides actual links to resources
- 📖 **Natural Citations**: "According to Cisco's documentation..." style

### **Production Ready**
- ☁️ **Multi-Platform**: Render.com ready, GCP portable
- 🔒 **Secure**: Environment variables for API keys
- ⚡ **Optimized**: Lazy loading, chunked processing
- 🎨 **Professional UI**: Modern Chainlit interface

## 📋 Prerequisites

- **Python 3.12** (PyTorch compatibility requirement)
- **Google API Key** (free from Google AI Studio)
- **SerpAPI Key** (optional, for web search)
- **uv** package manager (recommended) or pip

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd cisco-automation-certification-station

# Create virtual environment with Python 3.12
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Get API Keys

**Google Gemini API Key (Required):**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key

**SerpAPI Key (Optional):**
1. Visit [SerpAPI](https://serpapi.com/)
2. Sign up for free account
3. Get your API key from dashboard

### 3. Configure Environment
```bash
# Create .env file
touch .env

# Add your API keys
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env
echo "SERPAPI_KEY=your_serpapi_key_here" >> .env  # Optional
```

### 4. Build Vector Store
```bash
# Process documents and create embeddings
python vectorize.py
```

This will:
- Load 10 Cisco certification PDFs from `docs/`
- Fetch content from 9 official Cisco URLs
- Create 209 text chunks with 500-character chunking
- Build FAISS vector store in `rag/index/`

### 5. Run the Application

**Option A: Web Interface (Recommended)**
```bash
chainlit run app.py
```
Open http://localhost:8000 in your browser

**Option B: Command Line Interface**
```bash
python hybrid_rag_gpt.py
```

## 📁 Project Structure

```
cisco-automation-certification-station/
├── app.py                 # Chainlit web interface
├── hybrid_rag_gpt.py     # Core RAG logic with Gemini
├── vectorize.py          # Document processing & embedding
├── requirements.txt      # Python dependencies
├── render.yaml          # Render.com deployment config
├── urls.txt             # Official Cisco URLs to index
├── .env                 # API keys (create this)
├── docs/                # Cisco certification PDFs (10 files)
│   ├── 200-901-CCNAAUTO_v.1.1.pdf
│   ├── 300-435-ENAUTO-v2.0-7-9-2025.pdf
│   ├── 300-635-DCNAUTO-v2.0-7-9-2025.pdf
│   ├── 350-901-AUTOCOR-v2.0-7-9-2025.pdf
│   └── ... (6 more PDFs)
├── rag/
│   ├── vector_store.py   # FAISS vector store creation
│   ├── retriever.py     # Document retrieval with lazy loading
│   └── index/           # Generated vector store files
└── .chainlit/           # Chainlit configuration (auto-generated)
```

## 🧪 Testing the System

### Sample Questions to Try:

**Casual Interaction:**
```
User: Hi
AI: Hi! I'm here to help you with Cisco network automation certifications...
```

**Technical Questions:**
```
User: When will DevNet certs be retired?
AI: According to Cisco's official documentation, DevNet certifications will be retired on February 3, 2026...

User: Where can I prepare for CCNA automation?
AI: For Cisco certification preparation, I recommend these official resources:
- Cisco U (https://u.cisco.com/)
- Cisco Learning Network (https://learningnetwork.cisco.com/s/certifications)
...
```

## 🔧 Technical Details

### **Architecture Components:**

1. **Document Processing** (`vectorize.py`)
   - PDF extraction with PyPDF2
   - Web scraping with BeautifulSoup4
   - Text chunking (500 chars, 50 overlap)

2. **Vector Store** (`rag/vector_store.py`)
   - Sentence-transformers: `all-MiniLM-L6-v2`
   - FAISS IndexFlatL2 for similarity search
   - Lazy loading for efficiency

3. **Hybrid RAG** (`hybrid_rag_gpt.py`)
   - Intelligent routing (casual vs. technical)
   - Document search + web search
   - Google Gemini 1.5 Flash integration
   - Natural language generation

4. **Interfaces**
   - **Chainlit**: Modern web UI with chat history
   - **CLI**: Direct terminal interaction

### **Key Dependencies:**
```
chainlit              # Web interface
google-generativeai   # Gemini API client
sentence-transformers # Text embeddings
faiss-cpu            # Vector similarity search
python-dotenv        # Environment variables
torch                # ML framework
PyPDF2               # PDF processing
beautifulsoup4       # Web scraping
requests             # HTTP requests
numpy<2.0            # NumPy compatibility
google-search-results # SerpAPI client
```

## 🚀 Deployment

### **Google Cloud Run (Production Ready)**
Optimized for production deployment with auto-scaling, 2GB memory, and pay-per-use pricing:

#### **Prerequisites:**
1. Install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. Create a [Google Cloud Project](https://console.cloud.google.com/)
3. Enable billing for your project
4. Get your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

#### **Option 1: Automated Deployment (Recommended)**
```bash
# Authenticate with Google Cloud
gcloud auth login

# Run the deployment script (builds image + deploys)
./deploy-gcp.sh YOUR_PROJECT_ID
```

#### **Option 2: Quick Deploy (Use Pre-built Image)**
If you already have a built image or want to skip the build process:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Quick deploy with existing image (30-60 seconds)
gcloud run deploy cisco-automation-chatbot \
  --image gcr.io/YOUR_PROJECT_ID/cisco-automation-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars GOOGLE_API_KEY=your_google_api_key,EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2,PYTHONUNBUFFERED=1,TOKENIZERS_PARALLELISM=false
```

#### **Option 3: Build and Deploy Manually**
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Build container image (5-10 minutes)
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cisco-automation-chatbot

# Deploy to Cloud Run
gcloud run deploy cisco-automation-chatbot \
  --image gcr.io/YOUR_PROJECT_ID/cisco-automation-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --set-env-vars GOOGLE_API_KEY=your_google_api_key
```

#### **Production Features:**
- ⚡ **Auto-scaling**: 0-10 instances based on demand
- 💾 **Memory**: 2GB allocated (handles AI models efficiently)
- 💰 **Cost-effective**: Pay only for actual usage (~$0.05-0.50/month typical)
- 🔒 **Secure**: Built-in HTTPS and secret management
- 🌍 **Global**: Deploy to multiple regions worldwide
- 📊 **Monitoring**: Built-in logging, metrics, and alerting
- 🚀 **Performance**: Fast cold starts with optimized container

#### **After Deployment:**
Your chatbot will be available at: `https://cisco-automation-chatbot-[hash]-uc.a.run.app`

### **Alternative: Render.com**
*Note: Render has memory limitations (512MB) that may cause issues with AI models.*

The project includes `render.yaml` for deployment:
1. Fork this repository
2. Connect to Render.com
3. Add environment variables in Render dashboard
4. Deploy (may experience memory issues)

## 🛠️ Customization

### **Add More Documents:**
1. Place PDFs in `docs/` folder
2. Add URLs to `urls.txt`
3. Run `python vectorize.py` to rebuild index

### **Modify AI Behavior:**
Edit the `system_prompt` in `hybrid_rag_gpt.py`:

```python
system_prompt = (
    "You are a helpful AI assistant for [YOUR DOMAIN] preparation. "
    # Customize for your use case
)
```

### **Change Embedding Model:**
In `rag/vector_store.py`:

```python
model = SentenceTransformer("your-preferred-model")
```

## 🔍 Troubleshooting

### **Common Issues:**

**NumPy Compatibility Error:**
```bash
# Ensure Python 3.12 and NumPy < 2.0
python --version  # Should be 3.12.x
pip install "numpy<2.0"
```

**API Key Not Found:**
```bash
# Check .env file exists and has correct format
cat .env
# Should show: GOOGLE_API_KEY=your_key_here
```

**FAISS Loading Issues:**
```bash
# Rebuild vector store
rm -rf rag/index/
python vectorize.py
```

**Conda Environment Conflicts:**
```bash
# Disable conda auto-activation
conda config --set auto_activate_base false
```

## 📊 Performance

- **Document Processing**: ~17 seconds for 209 chunks
- **Query Response**: ~2-3 seconds (including vector search + AI generation)
- **Memory Usage**: ~500MB (with loaded models)
- **Storage**: ~50MB (vector store + models)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini** for free, high-quality AI responses
- **Cisco** for comprehensive certification documentation
- **Chainlit** for the beautiful chat interface
- **Sentence Transformers** for excellent embedding models
- **FAISS** for efficient vector similarity search

---

**Built with ❤️ for the Cisco certification community**

*This project demonstrates how to build production-ready RAG systems using free, open-source tools and APIs.*


