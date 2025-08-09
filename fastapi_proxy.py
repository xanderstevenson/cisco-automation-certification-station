#!/usr/bin/env python3
"""
FastAPI server that proxies requests to Streamlit
"""

import os
import time
import threading
import subprocess
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
import uvicorn
from pathlib import Path

app = FastAPI(title="Cisco Automation Certification Station")

# Global variables
streamlit_process = None
streamlit_ready = False

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
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    """Status endpoint to check if Streamlit is ready"""
    global streamlit_ready
    
    # Check if Streamlit is responding
    try:
        response = requests.get('http://localhost:8502/healthz', timeout=1)
        streamlit_ready = response.status_code == 200
    except:
        streamlit_ready = False
    
    return {
        "status": "ok",
        "streamlit_ready": streamlit_ready
    }

@app.get("/app")
@app.get("/app/{path:path}")
async def proxy_to_streamlit(path: str = "", request: Request = None):
    """Proxy requests to Streamlit"""
    global streamlit_ready
    
    # If Streamlit isn't ready yet, show a loading page
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
    target_url = f'http://localhost:8502/{path}'
    
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
    except Exception as e:
        print(f"Error proxying to Streamlit: {e}")
        return Response(
            content=f"Error connecting to the application: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

def start_streamlit():
    """Start Streamlit in the background"""
    global streamlit_process, streamlit_ready
    
    print("🚀 Starting Streamlit in background thread...")
    
    try:
        # Start Streamlit in a separate process
        streamlit_cmd = [
            "streamlit", "run", "app.py",
            "--server.port", "8502",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.fileWatcherType", "none"
        ]
        
        print(f"📡 Running Streamlit command: {' '.join(streamlit_cmd)}")
        
        # Start the Streamlit process
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
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

def start():
    """Start the FastAPI server with Streamlit in the background"""
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Start the FastAPI server
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start()
