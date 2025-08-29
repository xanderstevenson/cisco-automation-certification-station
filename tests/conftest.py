"""
Shared test fixtures and configuration for Cisco Automation Certification Station tests.
"""
import os
import pytest
from fastapi.testclient import TestClient
import sys
import tempfile

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi_only import app
from hybrid_rag_gpt import load_vector_store

@pytest.fixture
def test_client():
    """Create a test client for FastAPI application."""
    return TestClient(app)

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("SERPAPI_KEY", "test_serper_key")
    monkeypatch.setenv("EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")
    # Use a temporary directory for model cache
    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("TRANSFORMERS_CACHE", tmp_dir)
        monkeypatch.setenv("MODEL_CACHE_DIR", tmp_dir)
        yield

@pytest.fixture
def vector_store(tmp_path):
    """Initialize and return the vector store for testing."""
    os.environ["MODEL_CACHE_DIR"] = str(tmp_path)
    load_vector_store()
    return True

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing document processing."""
    return """
    CCNA Automation Exam Topics
    1.0 Network Fundamentals
    2.0 Network Access
    3.0 IP Connectivity
    4.0 IP Services
    5.0 Security Fundamentals
    6.0 Automation and Programmability
    """

@pytest.fixture
def sample_query():
    """Sample user query for testing RAG functionality."""
    return "What are the CCNA Automation exam topics?"

@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing context maintenance."""
    return [
        {"role": "user", "content": "What certifications are available?"},
        {"role": "assistant", "content": "Cisco offers several automation certifications including CCNA, CCNP, and CCIE Automation tracks."}
    ]