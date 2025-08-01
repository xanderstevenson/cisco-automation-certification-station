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
# Install PyTorch first (CPU-only)
RUN uv pip install --system torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu

# Install FAISS separately to avoid build issues
RUN uv pip install --system faiss-cpu==1.8.0 --only-binary=faiss-cpu

# Install remaining dependencies
RUN uv pip install --system -r requirements-lite.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Start command
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]
