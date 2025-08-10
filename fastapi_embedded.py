#!/usr/bin/env python3
"""
FastAPI server with embedded Streamlit UI
"""

import os
import sys
import asyncio
import uvicorn
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cisco Automation Certification Station")

# Mount static files directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
PORT = int(os.environ.get("PORT", 8080))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
STREAMLIT_SERVER = "http://localhost:8501"

# Create an async HTTP client
http_client = httpx.AsyncClient()

# HTML template for the loading page
LOADING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Loading Cisco Automation Certification Station</title>
    <meta http-equiv="refresh" content="2;url=/app" />
    <style>
        body { 
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }
        .loading-container {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 20px;
        }
        .spinner {
            border: 8px solid #f3f3f3;
            border-top: 8px solid #0D6EFD;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 2s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        h1, h2, h3 {
            color: #333;
            margin-top: 0;
        }
        p {
            color: #666;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="loading-container">
        <div class="spinner"></div>
        <h2>Loading Cisco Automation Certification Station</h2>
        <p>Please wait while we prepare your environment...</p>
        <p><small>This may take a moment on first load</small></p>
    </div>
</body>
</html>
"""

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# Status endpoint
@app.get("/status")
async def status_check():
    return {"status": "ok", "streamlit_ready": True}

# Root endpoint - redirect to loading page
@app.get("/")
async def root():
    return HTMLResponse(content=LOADING_HTML, status_code=200)

# Proxy for Streamlit static files and WebSocket
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_streamlit(path: str, request: Request):
    # Forward all requests to Streamlit server
    url = f"{STREAMLIT_SERVER}/{path}"
    
    try:
        # Get the request body if present
        body = await request.body() if request.method in ["POST", "PUT"] else None
        
        # Forward headers
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        
        # Make the request to Streamlit
        response = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=30.0
        )
        
        # Return the response from Streamlit
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except Exception as e:
        logger.error(f"Error proxying to Streamlit: {str(e)}")
        return Response(
            content=f"Error connecting to Streamlit server: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

# Start Streamlit in a separate process
async def start_streamlit():
    import subprocess
    import sys
    
    # Command to start Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--server.fileWatcherType", "none",
        "--server.address", "0.0.0.0"
    ]
    
    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Log Streamlit output
    for line in process.stdout:
        logger.info(f"[Streamlit] {line.strip()}")
    
    return process

def start_server():
    """Start the FastAPI server"""
    import uvicorn
    import threading
    import time
    
    # Start Streamlit in a separate thread
    def run_streamlit():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_streamlit())
    
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Give Streamlit a moment to start
    time.sleep(2)
    
    # Start the FastAPI server
    logger.info(f"🚀 Starting FastAPI server on port {PORT}...")
    uvicorn.run(
        "fastapi_embedded:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info" if not DEBUG else "debug",
        reload=DEBUG,
        workers=1,
    )

if __name__ == "__main__":
    start_server()
