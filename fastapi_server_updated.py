#!/usr/bin/env python3
"""
FastAPI server with Streamlit integration for Cisco Automation Certification Station
"""

import os
import time
import threading
import subprocess
import logging
import signal
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cisco Automation Certification Station")

# Global variables
streamlit_process = None
streamlit_ready = False

# Load environment variables
PORT = int(os.environ.get("PORT", 8080))
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", 8501))
STREAMLIT_HOST = os.environ.get("STREAMLIT_HOST", "0.0.0.0")

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

# Error page template
ERROR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Error Loading Application</title>
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
        .error-container {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 20px;
        }
        .error-icon {
            color: #dc3545;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #dc3545;
            margin-top: 0;
        }
        p {
            color: #666;
            line-height: 1.5;
        }
        .retry-button {
            display: inline-block;
            background: #0D6EFD;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            margin-top: 1rem;
        }
        .retry-button:hover {
            background: #0b5ed7;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h2>Error Loading Application</h2>
        <p>We're having trouble connecting to the application. Please try again in a moment.</p>
        <p><small>Error: {error_message}</small></p>
        <a href="/" class="retry-button">Try Again</a>
    </div>
</body>
</html>
"""

@app.get("/")
async def root():
    """Serve the loading page"""
    return HTMLResponse(content=LOADING_HTML)

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    """Status endpoint to check if Streamlit is ready"""
    global streamlit_ready
    
    # Check if Streamlit is responding
    try:
        response = requests.get(f'http://{STREAMLIT_HOST}:{STREAMLIT_PORT}/healthz', timeout=1)
        streamlit_ready = response.status_code == 200
        return {
            "status": "ok",
            "streamlit_ready": streamlit_ready,
            "streamlit_status": response.status_code
        }
    except Exception as e:
        streamlit_ready = False
        return {
            "status": "error",
            "streamlit_ready": False,
            "error": str(e)
        }

def start_streamlit():
    """Start Streamlit in the background"""
    global streamlit_process, streamlit_ready
    
    logger.info(f"🚀 Starting Streamlit in background thread on {STREAMLIT_HOST}:{STREAMLIT_PORT}...")
    
    try:
        # Start Streamlit in a separate process
        streamlit_cmd = [
            "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", STREAMLIT_HOST,
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.fileWatcherType", "none",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light",
            "--theme.primaryColor", "#0D6EFD",
            "--theme.backgroundColor", "#FFFFFF",
            "--theme.secondaryBackgroundColor", "#F8F9FA",
            "--theme.textColor", "#000000",
            "--theme.font", "sans serif"
        ]
        
        logger.info(f"📡 Running Streamlit command: {' '.join(streamlit_cmd)}")
        
        # Set up environment variables for Streamlit
        env = os.environ.copy()
        env["STREAMLIT_SERVER_PORT"] = str(STREAMLIT_PORT)
        env["STREAMLIT_SERVER_ADDRESS"] = STREAMLIT_HOST
        env["STREAMLIT_SERVER_HEADLESS"] = "true"
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        
        # Start the Streamlit process
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        logger.info(f"🔄 Streamlit process started with PID: {streamlit_process.pid}")
        
        # Monitor the Streamlit process
        for line in iter(streamlit_process.stdout.readline, ''):
            line = line.strip()
            if line:
                logger.info(f"[Streamlit] {line}")
                
                # Check if Streamlit is ready
                if "You can now view your Streamlit app in your browser" in line:
                    logger.info("✅ Streamlit is ready!")
                    streamlit_ready = True
        
        # If we get here, the process has ended
        if streamlit_process.poll() is not None:
            logger.error(f"❌ Streamlit process ended with return code: {streamlit_process.returncode}")
            streamlit_ready = False
            
    except Exception as e:
        logger.error(f"❌ Error starting Streamlit: {e}")
        import traceback
        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        streamlit_ready = False

@app.get("/app")
@app.get("/app/{path:path}")
async def proxy_to_streamlit(path: str = "", request: Request = None):
    """Proxy requests to the Streamlit app"""
    global streamlit_ready
    
    # Build the target URL for Streamlit
    target_url = f'http://{STREAMLIT_HOST}:{STREAMLIT_PORT}/{path}'
    
    # Add query parameters if any
    if request and request.query_params:
        query_string = str(request.query_params)
        target_url = f"{target_url}?{query_string}"
    
    try:
        # Forward the request to Streamlit
        response = requests.get(
            target_url,
            headers={"Host": request.headers.get("host", "")},
            timeout=10
        )
        
        # Get the content type from the response
        content_type = response.headers.get('content-type', 'text/html')
        
        # Return the response from Streamlit
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=content_type,
            headers={
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Connection error while proxying to Streamlit: {e}")
        streamlit_ready = False
        return HTMLResponse(
            content=ERROR_HTML.format(error_message="Connection to the application failed. Please try again in a moment."),
            status_code=503
        )
    except Exception as e:
        logger.error(f"❌ Error proxying to Streamlit: {e}")
        return HTMLResponse(
            content=ERROR_HTML.format(error_message=str(e)),
            status_code=500
        )

def signal_handler(sig, frame):
    """Handle termination signals to clean up processes"""
    global streamlit_process
    
    logger.info("\n🚦 Received shutdown signal. Cleaning up...")
    
    # Terminate Streamlit process if it's running
    if streamlit_process and streamlit_process.poll() is None:
        logger.info("🛑 Stopping Streamlit process...")
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Streamlit process did not terminate gracefully, forcing...")
            streamlit_process.kill()
    
    logger.info("👋 Shutdown complete.")
    sys.exit(0)

def start():
    """Start the FastAPI server with Streamlit in the background"""
    # Set up signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Start the FastAPI server
    logger.info(f"🚀 Starting FastAPI server on port {PORT}...")
    logger.info(f"🔌 Streamlit will be available at: http://0.0.0.0:{PORT}/app")
    
    uvicorn.run(
        "fastapi_server_updated:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        reload=False,
        workers=1
    )

if __name__ == "__main__":
    start()
