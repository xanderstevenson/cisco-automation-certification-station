#!/usr/bin/env python3
"""
Simplified FastAPI server to serve the loading page and proxy to Streamlit
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import subprocess
import threading
import time
import os
import uvicorn
from pathlib import Path

app = FastAPI(title="Cisco Automation Certification Station")

# Global variable to track if Streamlit is ready
streamlit_ready = False
streamlit_process = None

@app.get("/")
async def root():
    """Serve the loading page with auto-refresh"""
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
    global streamlit_ready, streamlit_process
    
    # Check if Streamlit is responding
    streamlit_responding = False
    try:
        import requests
        response = requests.get('http://localhost:8502/healthz', timeout=1)
        streamlit_responding = response.status_code == 200
    except:
        pass
    
    return {
        "status": "ok",
        "streamlit_ready": streamlit_ready,
        "streamlit_responding": streamlit_responding
    }

def start_streamlit():
    """Start Streamlit app in the background"""
    global streamlit_ready, streamlit_process
    
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

@app.get("/app")
@app.get("/app/{path:path}")
async def streamlit_proxy(path: str = ""):
    """Proxy requests to the Streamlit app"""
    import requests
    
    # Build the target URL for Streamlit
    streamlit_url = f'http://localhost:8502/{path}'
    
    try:
        # Forward the request to Streamlit
        response = requests.get(streamlit_url, timeout=10)
        
        # Return the response from Streamlit
        return HTMLResponse(
            content=response.text,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        print(f"❌ Error proxying to Streamlit: {e}")
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error Loading Application</title>
            <meta http-equiv="refresh" content="5" />
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
                h1, h2, h3 {
                    color: #dc3545;
                    margin-top: 0;
                }
                p {
                    color: #666;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>Error Loading Application</h2>
                <p>We're having trouble connecting to the application. Please wait while we try to reconnect...</p>
                <p><small>This page will automatically refresh in a few seconds.</small></p>
            </div>
        </body>
        </html>
        """, status_code=503)

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
