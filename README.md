<div align="center">
  <img src="public/Cisco-automation-certification-station.png" alt="Cisco Automation Certification Station">
</div>


A production-ready Hybrid Retrieval-Augmented Generation (RAG) system designed for Cisco network automation certification preparation. This system combines local document search, web search, and AI generation to provide comprehensive, source-backed answers for:

- [CCNA Automation](https://learningnetwork.cisco.com/s/ccnaauto-exam-topics)
- [CCNP Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf)
- [CCIE Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf)
- [Automating Cisco Enterprise Solutions (ENAUTO)](https://www.cisco.com/site/us/en/learn/training-certifications/exams/enauto.html)
- [Automating Cisco Data Center Networking Solutions (DCNAUTO)](https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf)


## What This System Does

This application serves as an intelligent certification advisor that:

- **Processes Official Documentation**: Ingests 10+ official Cisco certification PDFs and URLs
- **Provides Expert Guidance**: Answers technical questions with specific exam topics and study plans
- **Combines Multiple Sources**: Uses both local document search and real-time web search
- **Delivers Fast Responses**: Optimized with parallel processing and efficient AI models
- **Offers Professional Interface**: Clean web UI with Cisco branding and responsive design

## System Architecture

### Hybrid RAG Architecture Overview

```mermaid
flowchart TD
    A[👤 User Query] --> B{🧠 Intelligent Router}
    
    B -->|Casual Greeting| C[💬 Direct Response]
    B -->|Technical Question| D[🔍 Hybrid RAG Pipeline]
    
    C --> E[✅ Quick Reply]
    
    D --> F[📚 Document Search]
    D --> G[🌐 Web Search]
    
    F --> H[(🗂️ FAISS Vector Store<br/>209 Chunks)]
    G --> I[🔎 SerpAPI<br/>Real-time Results]
    
    H --> J[🔗 Context Fusion]
    I --> J
    
    J --> K[🤖 Google Gemini<br/>1.5 Flash AI]
    
    K --> L[📋 Comprehensive Response<br/>• Technical Details<br/>• Source Citations<br/>• Study Plans<br/>• Learning Paths]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style D fill:#f3e5f5
    style K fill:#e8f5e8
    style L fill:#fff8e1
```

### System Components Architecture

```mermaid
graph TB
    subgraph "🖥️ Frontend Layer"
        UI[Chainlit Web Interface<br/>• Chat History<br/>• File Upload<br/>• Cisco Theme]
    end
    
    subgraph "⚙️ Processing Layer"
        ROUTER[Query Router<br/>• Intent Classification<br/>• Route Selection]
        RAG[Hybrid RAG Engine<br/>• Parallel Processing<br/>• Context Fusion]
    end
    
    subgraph "🤖 AI & Data Layer"
        GEMINI[Google Gemini 1.5 Flash<br/>• Text Generation<br/>• Context Aware<br/>• Fast Response]
        SERP[SerpAPI<br/>• Real-time Search<br/>• Current Information]
    end
    
    subgraph "💾 Storage Layer"
        VECTOR[(FAISS Vector Store<br/>• 384-dim Embeddings<br/>• Fast Similarity Search)]
        DOCS[(Document Collection<br/>• 11 Cisco PDFs<br/>• 9 Official URLs)]
        CONFIG[(Configuration<br/>• Environment Variables<br/>• Model Settings)]
    end
    
    UI --> ROUTER
    ROUTER --> RAG
    RAG --> GEMINI
    RAG --> SERP
    RAG --> VECTOR
    VECTOR --> DOCS
    RAG --> CONFIG
    
    style UI fill:#e3f2fd
    style ROUTER fill:#fff3e0
    style RAG fill:#f3e5f5
    style GEMINI fill:#e8f5e8
    style VECTOR fill:#fce4ec
    style DOCS fill:#f1f8e9
```

### Document Processing Pipeline

The system processes documents through a sophisticated vectorization pipeline:

**📁 Data Sources:**
- 11 official Cisco certification PDFs (CCNA Auto, ENAUTO, DCNAUTO, AUTOCOR, CCIE materials)
- 9 curated Cisco URLs (Cisco U courses, Learning Network, DevNet resources)

**🔄 Processing Steps:**
1. **Content Extraction**: PyPDF2 for PDFs, BeautifulSoup4 for web content
2. **Text Chunking**: 500 characters per chunk with 50-character overlap for context preservation
3. **Embedding Generation**: paraphrase-MiniLM-L3-v2 model creates 384-dimensional vectors
4. **Vector Store Creation**: FAISS IndexFlatL2 for fast similarity search

**📊 Output:**
- `faiss.index` (321KB) - Vector similarity search index
- `texts.pkl` (101KB) - Text chunks and metadata
- 209 total chunks ready for sub-second query response

## Technical Components

The system is built using the following key technologies:

### Core Framework
- **Python 3.12**: Required for PyTorch compatibility and optimal performance
- **Chainlit**: Modern web interface for chat applications with real-time streaming
- **Google Gemini 1.5 Flash**: Fast, free AI model for response generation
- **FAISS**: Facebook AI Similarity Search for efficient vector operations
- **Sentence Transformers**: State-of-the-art text embedding models

### Document Processing
- **PyPDF2**: PDF text extraction and metadata handling
- **BeautifulSoup4**: Web content scraping and HTML parsing
- **Requests**: HTTP client for web content retrieval

### Search and Retrieval
- **SerpAPI**: Real-time Google search integration (optional)
- **Concurrent.futures**: Parallel processing for faster response times
- **Pickle**: Efficient serialization for text chunk storage

### Deployment
- **Docker**: Containerization for consistent deployment
- **Google Cloud Run**: Serverless container platform with auto-scaling
- **UV Package Manager**: Fast Python package installation and management

## Prerequisites

Before setting up this system, ensure you have:

- **Python 3.12**: Required for PyTorch compatibility and optimal performance
- **Google API Key**: Free from Google AI Studio for Gemini API access
- **SerpAPI Key**: Optional for web search integration (free tier available)
- **Git**: For cloning the repository
- **UV Package Manager**: Recommended for faster dependency installation (or pip as fallback)

## Step-by-Step Setup Instructions

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/xanderstevenson/cisco-automation-certification-station.git
cd cisco-automation-certification-station
```

### Step 2: Set Up Python Environment

**Option A: Using UV (Recommended)**
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with Python 3.12
uv venv --python 3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

**Option B: Using Standard pip**
```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Obtain API Keys

**Google Gemini API Key (Required)**

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the generated API key

**SerpAPI Key (Optional - for web search)**

1. Visit [SerpAPI](https://serpapi.com/)
2. Sign up for a free account (100 searches/month)
3. Navigate to your dashboard
4. Copy your API key

### Step 4: Configure Environment Variables

```bash
# Create .env file in the project root
touch .env

# Add your API keys to .env file
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env
echo "SERPAPI_KEY=your_serpapi_key_here" >> .env  # Optional
echo "EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2" >> .env
echo "PYTHONUNBUFFERED=1" >> .env
echo "TOKENIZERS_PARALLELISM=false" >> .env
```

**Example .env file:**
```env
GOOGLE_API_KEY=AIzaSyAepQxUh3yx0W5j70oKOMQNqnsgRcS6TCU
SERPAPI_KEY=your_serpapi_key_here
EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2
PYTHONUNBUFFERED=1
TOKENIZERS_PARALLELISM=false
```

### Step 5: Build the Knowledge Base

```bash
# Process documents and create vector embeddings
python vectorize.py
```

**What this does:**

- Loads 10 Cisco certification PDFs from the `docs/` directory
- Fetches content from 9 official Cisco URLs listed in `urls.txt`
- Chunks all content into 209 text segments (500 chars each, 50 char overlap)
- Creates vector embeddings using the paraphrase-MiniLM-L3-v2 model
- Builds FAISS index for fast similarity search
- Saves index files to `rag/index/` directory

**Expected output:**

```text
Loading documents from docs/...
Processed 10 PDF files
Fetching content from URLs...
Processed 9 web URLs
Creating text chunks...
Generated 209 text chunks
Building vector embeddings...
Created FAISS index with 209 vectors
Saved to rag/index/faiss.index (321KB)
Saved to rag/index/texts.pkl (101KB)
Vectorization complete!
```

### Step 6: Run the Application

**Option A: Web Interface (Recommended)**
```bash
# Start the Chainlit web interface
chainlit run app.py
```

The application will start at `http://localhost:8000`

**Option B: Command Line Interface**
```bash
# Run the command-line version
python hybrid_rag_gpt.py
```

### Step 7: Test the System

Try these sample queries to verify everything is working:

**Casual Interaction:**
```
User: Hi
Expected: Brief greeting and offer to help with Cisco certifications
```

**Technical Questions:**
```
User: When will DevNet certifications be retired?
Expected: Detailed response with February 3, 2026 date and context

User: How do I prepare for CCNA Automation?
Expected: Comprehensive study plan with specific exam topics and Cisco U links

User: What's the difference between NETCONF and RESTCONF?
Expected: Technical comparison with protocol details and use cases
```

## Project Structure

```
cisco-automation-certification-station/
├── README.md                    # This comprehensive guide
├── requirements.txt             # Python dependencies
├── requirements-lite.txt        # Memory-optimized dependencies for deployment
├── .env                         # Environment variables (create this)
├── .gitignore                   # Git ignore rules
├── render.yaml                  # Render.com deployment configuration
├── Dockerfile                   # Docker containerization
├── deploy-gcp.sh               # Google Cloud Run deployment script
│
├── app.py                       # Chainlit web interface entry point
├── hybrid_rag_gpt.py           # Core RAG logic with Gemini integration
├── vectorize.py                # Document processing and embedding creation
├── urls.txt                    # Official Cisco URLs for knowledge base
│
├── docs/                       # Cisco certification PDFs (10 files)
│   ├── 200-901-CCNAAUTO_v.1.1.pdf
│   ├── 300-435-ENAUTO-v2.0-7-9-2025.pdf
│   ├── 300-635-DCNAUTO-v2.0-7-9-2025.pdf
│   ├── 350-901-AUTOCOR-v2.0-7-9-2025.pdf
│   ├── CCIE_Automation_Lab_V1.1_BP.pdf
│   ├── CCIE_Automation_equipment_list_v1.1.pdf
│   ├── Automation-Certification&Learning-Update.pdf
│   ├── Cisco-Certifications-Portfolio-Updates.pdf
│   ├── Learn-with-Cisco-evolving.pdf
│   └── cisco-certification-career-path.pdf
│
├── rag/                        # RAG system components
│   ├── __init__.py
│   ├── vector_store.py         # FAISS vector store creation
│   ├── retriever.py           # Document retrieval with lazy loading
│   └── index/                  # Generated vector store files
│       ├── faiss.index         # FAISS similarity search index (321KB)
│       └── texts.pkl           # Text chunks and metadata (101KB)
│
├── public/                     # Static files for Chainlit UI
│   ├── Cisco-automation-certification-station.png
│   ├── Automation_Cert_badges_Current_Future.png
│   └── cisco-theme.css         # Custom Cisco blue theme
│
├── .chainlit/                  # Chainlit configuration
│   ├── config.toml            # UI customization and settings
│   └── translations/          # Internationalization files
│
└── .venv/                      # Virtual environment (created during setup)
    └── ...
```

## Deployment Options

### Option 1: Google Cloud Run (Recommended for Production)

Google Cloud Run provides the best performance, scalability, and integration with the Google Gemini API.

**Quick Deploy:**
```bash
# Set your Google Cloud project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Build and deploy in one command
gcloud builds submit --tag gcr.io/$PROJECT_ID/cisco-automation-chatbot
gcloud run deploy cisco-automation-certification-station \
  --image gcr.io/$PROJECT_ID/cisco-automation-chatbot \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --set-env-vars GOOGLE_API_KEY=your_api_key,EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2
```

**Features:**
- Auto-scaling from 0 to 10 instances based on demand
- 2GB memory allocation for AI models
- Pay-per-use pricing (~$0.05-0.50/month typical usage)
- Built-in HTTPS and global CDN
- Integrated logging and monitoring

### Option 2: Local Development

**For development and testing:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the web interface
chainlit run app.py

# Or run command-line version
python hybrid_rag_gpt.py
```

### Option 3: Render.com (Alternative)

**Note**: Render's free tier has memory limitations (512MB) that may cause issues with AI models.

```bash
# The project includes render.yaml for deployment
# 1. Fork this repository
# 2. Connect to Render.com
# 3. Add environment variables in dashboard:
#    - GOOGLE_API_KEY
#    - SERPAPI_KEY (optional)
# 4. Deploy
```

## Performance Characteristics

### Response Times
- **Casual greetings**: ~1-2 seconds (direct response)
- **Technical queries**: ~6-8 seconds (hybrid RAG pipeline)
- **Document search**: ~0.5 seconds (FAISS vector similarity)
- **Web search**: ~2-3 seconds (SerpAPI + parallel processing)
- **AI generation**: ~3-4 seconds (Gemini 1.5 Flash)

### Resource Usage
- **Memory**: ~450MB (with loaded models)
- **Storage**: ~50MB (vector store + dependencies)
- **CPU**: Minimal during idle, burst during query processing
- **Network**: ~1-2MB per query (including web search)

### Scalability
- **Concurrent users**: 10-50 (depending on deployment)
- **Query throughput**: ~10-20 queries/minute per instance
- **Knowledge base**: Supports 1000+ documents with current architecture
- **Response quality**: Maintains consistency across scale

## Troubleshooting

### Common Issues and Solutions

**1. NumPy Compatibility Error**
```bash
# Error: numpy version incompatible with PyTorch
# Solution: Ensure Python 3.12 and NumPy < 2.0
python --version  # Should show 3.12.x
pip install "numpy<2.0"
```

**2. API Key Not Found**
```bash
# Error: GOOGLE_API_KEY not found
# Solution: Check .env file format
cat .env
# Should show: GOOGLE_API_KEY=your_key_here (no quotes, no spaces)
```

**3. FAISS Loading Issues**
```bash
# Error: could not open faiss.index for reading
# Solution: Rebuild vector store
rm -rf rag/index/
python vectorize.py
```

**4. Conda Environment Conflicts**
```bash
# Error: conda interfering with virtual environment
# Solution: Disable conda auto-activation
conda config --set auto_activate_base false
# Restart terminal and recreate virtual environment
```

**5. Memory Issues During Deployment**
```bash
# Error: Out of memory during Docker build
# Solution: Use requirements-lite.txt for deployment
cp requirements-lite.txt requirements.txt
# Or increase deployment memory allocation
```

**6. Slow Response Times**
```bash
# Issue: Responses taking >15 seconds
# Solutions:
# 1. Check internet connection for web search
# 2. Verify SERPAPI_KEY is valid
# 3. Monitor system resources
# 4. Consider disabling web search for faster responses
```

**7. PDF Processing Errors**
```bash
# Error: Cannot extract text from PDF
# Solution: Ensure PDFs are text-based (not scanned images)
# Check PDF file integrity:
python -c "import PyPDF2; print('PDF library working')"
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Add to .env file
echo "DEBUG=true" >> .env
echo "PYTHONUNBUFFERED=1" >> .env

# Run with verbose output
python hybrid_rag_gpt.py
```

### Getting Help

1. **Check logs**: Look for error messages in terminal output
2. **Verify setup**: Ensure all prerequisites are installed
3. **Test components**: Run vectorization and API calls separately
4. **Check resources**: Monitor memory and CPU usage
5. **Update dependencies**: Ensure all packages are current versions

## Customization Guide

### Adding New Documents

```bash
# 1. Add PDFs to docs/ directory
cp your-new-cert.pdf docs/

# 2. Add URLs to urls.txt
echo "https://cisco.com/your-new-resource" >> urls.txt

# 3. Rebuild vector store
python vectorize.py
```

### Modifying AI Behavior

Edit the system prompt in `hybrid_rag_gpt.py`:

```python
system_prompt = """
You are a helpful AI assistant specialized in [YOUR DOMAIN].

**Your expertise includes:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Communication style:**
- [Your preferred style]
- [Response format]

**Learning Resource Recommendations:**
1. [Primary resource]
2. [Secondary resource]
3. [Tertiary resource]
"""
```

### Changing Embedding Model

In `rag/vector_store.py`:

```python
# Options: paraphrase-MiniLM-L3-v2 (fast, 384-dim)
#          all-MiniLM-L6-v2 (balanced, 384-dim)
#          all-mpnet-base-v2 (best quality, 768-dim)
model = SentenceTransformer("your-preferred-model")
```

### UI Customization

Modify `public/cisco-theme.css` for custom branding:

```css
:root {
  --primary-color: #your-brand-color;
  --secondary-color: #your-accent-color;
}
```

## Contributing

Contributions are welcome! Please follow these steps:

```bash
# 1. Fork the repository
git clone https://github.com/your-username/cisco-automation-certification-station.git

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
python vectorize.py  # Test document processing
chainlit run app.py  # Test web interface

# 4. Commit changes
git add .
git commit -m "Add amazing feature: detailed description"

# 5. Push and create pull request
git push origin feature/amazing-feature
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Google Gemini**: Fast, free AI model for response generation
- **Cisco**: Comprehensive certification documentation and learning resources
- **Chainlit**: Modern chat interface framework
- **FAISS**: Efficient vector similarity search
- **Sentence Transformers**: State-of-the-art text embedding models
- **Open Source Community**: For the excellent tools and libraries that make this possible

---

**Built for the Cisco certification community**

*This project demonstrates how to build production-ready RAG systems using free, open-source tools and APIs. It serves as both a practical certification study tool and a technical reference for implementing hybrid RAG architectures.*
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


