"""
Tests for FastAPI endpoints and API functionality.
"""
import pytest
from fastapi.testclient import TestClient

def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_status_check(test_client):
    """Test the status check endpoint."""
    response = test_client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "models_loaded" in data

def test_chat_endpoint_empty_message(test_client):
    """Test chat endpoint with empty message."""
    response = test_client.post("/chat", json={"message": ""})
    assert response.status_code == 400
    assert "error" in response.json()

def test_chat_endpoint_valid_message(test_client, mock_env):
    """Test chat endpoint with valid message."""
    # First check status - we expect models not to be loaded in test
    status = test_client.get("/status").json()
    if not status.get("models_loaded"):
        response = test_client.post("/chat", json={
            "message": "What are the CCNA Automation exam topics?",
            "conversation_history": []
        })
        assert response.status_code == 503  # Service Unavailable is correct when models aren't loaded
        assert "error" in response.json()
        assert "Models are still loading" in response.json()["error"]
    else:
        pytest.skip("Test assumes models are not loaded")

def test_chat_endpoint_with_history(test_client, mock_env):
    """Test chat endpoint with conversation history."""
    # First check status - we expect models not to be loaded in test
    status = test_client.get("/status").json()
    if not status.get("models_loaded"):
        response = test_client.post("/chat", json={
            "message": "Tell me more about that",
            "conversation_history": [
                {"role": "user", "content": "What certifications are available?"},
                {"role": "assistant", "content": "Cisco offers several automation certifications."}
            ]
        })
        assert response.status_code == 503  # Service Unavailable is correct when models aren't loaded
        assert "error" in response.json()
        assert "Models are still loading" in response.json()["error"]
    else:
        pytest.skip("Test assumes models are not loaded")

def test_chat_endpoint_invalid_json(test_client):
    """Test chat endpoint with invalid JSON."""
    response = test_client.post(
        "/chat",
        headers={"Content-Type": "application/json"},
        content="invalid json"
    )
    assert response.status_code in [400, 422]  # Both are acceptable for invalid JSON
    assert "error" in response.json() or "detail" in response.json()

def test_static_files(test_client):
    """Test static files are served correctly."""
    response = test_client.get("/public/Cisco-automation-certification-station.png")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

def test_main_app_html(test_client):
    """Test main application HTML is served correctly."""
    response = test_client.get("/app")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Cisco Automation Certification Station" in response.text

@pytest.mark.parametrize("endpoint", [
    "/nonexistent",
    "/api/v1/unknown",
    "/chat/invalid"
])
def test_404_handling(test_client, endpoint):
    """Test 404 error handling for unknown endpoints."""
    response = test_client.get(endpoint)
    assert response.status_code == 404