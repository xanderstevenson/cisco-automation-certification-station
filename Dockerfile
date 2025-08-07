# Use Python 3.12 slim image for better performance and smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false
ENV PORT=8080

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    swig \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy requirements first for better Docker layer caching
COPY requirements-lite.txt .

# Install Python dependencies with uv (much faster)
# Install PyTorch first (CPU-only) - Updated for uint64 compatibility
RUN uv pip install --system torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# Install FAISS separately to avoid build issues
RUN uv pip install --system faiss-cpu==1.8.0 --only-binary=faiss-cpu

# Install remaining dependencies
RUN uv pip install --system -r requirements-lite.txt

# Copy application code (including vector store files from git)
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Create simple startup script using only Python (no extra packages needed)
RUN echo '#!/bin/bash' > start.sh && \
    echo '# Start HTTP server for loading page immediately' >> start.sh && \
    echo 'python3 -m http.server 8080 --bind 0.0.0.0 &' >> start.sh && \
    echo 'HTTP_PID=$!' >> start.sh && \
    echo 'sleep 3' >> start.sh && \
    echo '# Start Streamlit on different port' >> start.sh && \
    echo 'streamlit run streamlit_app.py --server.port=8081 --server.address=0.0.0.0 --server.headless=true --server.fileWatcherType=none --browser.gatherUsageStats=false &' >> start.sh && \
    echo 'STREAMLIT_PID=$!' >> start.sh && \
    echo '# Wait for Streamlit to be ready (simple approach)' >> start.sh && \
    echo 'sleep 15' >> start.sh && \
    echo '# Kill HTTP server and redirect to Streamlit' >> start.sh && \
    echo 'kill $HTTP_PID' >> start.sh && \
    echo '# Use Python to forward port 8080 to 8081' >> start.sh && \
    echo 'python3 -c "import socket, threading; s=socket.socket(); s.bind((\"0.0.0.0\", 8080)); s.listen(5); [threading.Thread(target=lambda c: [c.connect((\"localhost\", 8081)), c.close()], args=(socket.socket(),)).start() for _ in iter(lambda: s.accept()[0], None)]" &' >> start.sh && \
    echo 'wait' >> start.sh && \
    chmod +x start.sh

# Create index.html that shows loading.html immediately
RUN echo '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=loading.html"><title>Loading...</title></head><body><script>window.location.href="loading.html";</script></body></html>' > index.html

# Start command using our script
CMD ["./start.sh"]
