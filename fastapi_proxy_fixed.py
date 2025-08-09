#!/usr/bin/env python3
"""
Fixed FastAPI proxy server for Streamlit with improved error handling
"""

import os
import time
import threading
import subprocess
import requests
import socket
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response, JSONResponse
import uvicorn
from pathlib import Path

app = FastAPI(title="Cisco Automation Certification Station")

# Configuration
STREAMLIT_PORT = 8502
STREAMLIT_HOST = "0.0.0.0"  # Changed from localhost to 0.0.0.0
STREAMLIT_URL = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"

# Global variables
streamlit_process = None
streamlit_ready = False

# Helper function to check if a port is open
def is_port_open(port, host='localhost', timeout=1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except:
        return False

@app.get("/")
async def root():
    """Serve the loading page"""
    return HTMLResponse("""
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
    """)

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok", "streamlit_ready": streamlit_ready}

@app.get("/status")
async def status_check():
    """Status endpoint to check if Streamlit is ready"""
    global streamlit_ready
    
    # Check if Streamlit is responding
    try:
        response = requests.get(f'{STREAMLIT_URL}/healthz', timeout=1)
        streamlit_ready = response.status_code == 200
        return {
            "status": "ok",
            "streamlit_ready": streamlit_ready,
            "streamlit_status": response.status_code if 'response' in locals() else "not_responding"
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
    
    print(f"🚀 Starting Streamlit in background thread on {STREAMLIT_HOST}:{STREAMLIT_PORT}...")
    
    try:
        # Start Streamlit in a separate process
        streamlit_cmd = [
            "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", STREAMLIT_HOST,  # Changed to 0.0.0.0
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.fileWatcherType", "none"
        ]
        
        print(f"📡 Running Streamlit command: {' '.join(streamlit_cmd)}")
        
        # Set environment variables for Streamlit
        env = os.environ.copy()
        env["STREAMLIT_SERVER_PORT"] = str(STREAMLIT_PORT)
        env["STREAMLIT_SERVER_ADDRESS"] = STREAMLIT_HOST
        
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
        
        print(f"🔄 Streamlit process started with PID: {streamlit_process.pid}")
        
        # Monitor the Streamlit process
        for line in iter(streamlit_process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(f"[Streamlit] {line}")
                
                # Check if Streamlit is ready
                if "You can now view your Streamlit app in your browser" in line:
                    print("✅ Streamlit is ready!")
                    streamlit_ready = True
        
        # If we get here, the process has ended
        if streamlit_process.poll() is not None:
            print(f"❌ Streamlit process ended with return code: {streamlit_process.returncode}")
            streamlit_ready = False
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        streamlit_ready = False

@app.get("/app")
@app.get("/app/{path:path}")
async def proxy_to_streamlit(path: str = "", request: Request = None):
    """Proxy requests to Streamlit"""
    global streamlit_ready
    
    # If Streamlit isn't ready yet, show a loading page
    if not streamlit_ready:
        # Check if Streamlit is running but not marked as ready
        try:
            response = requests.get(f'{STREAMLIT_URL}/healthz', timeout=1)
            if response.status_code == 200:
                streamlit_ready = True
                print("✅ Streamlit is now ready!")
        except:
            pass
            
        if not streamlit_ready:
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Loading Application</title>
                <meta http-equiv="refresh" content="2" />
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
                    <h2>Almost there...</h2>
                    <p>Preparing the Cisco Automation Certification Station.</p>
                    <p><small>This should only take a moment...</small></p>
                </div>
            </body>
            </html>
            """)
    
    # Build the target URL for Streamlit
    target_url = f'{STREAMLIT_URL}/{path}'
    
    # Forward query parameters if any
    if request and request.query_params:
        query_string = str(request.query_params)
        target_url = f"{target_url}?{query_string}"
    
    try:
        # Forward the request to Streamlit
        response = requests.get(target_url, timeout=10)
        
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
        print(f"❌ Connection error while proxying to Streamlit: {e}")
        streamlit_ready = False
        return Response(
            content=f"Error connecting to the application: {str(e)}",
            status_code=503,
            media_type="text/plain"
        )
    except Exception as e:
        print(f"❌ Error proxying to Streamlit: {e}")
        return Response(
            content=f"Error connecting to the application: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

def start():
    """Start the FastAPI server with Streamlit in the background"""
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Start the FastAPI server
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting FastAPI server on port {port}...")
    print(f"🔌 Streamlit will be available at {STREAMLIT_URL}")
    
    # Start the server with auto-reload in development
    uvicorn.run(
        "fastapi_proxy_fixed:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    start()
