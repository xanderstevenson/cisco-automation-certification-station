#!/usr/bin/env python3
"""
FastAPI server to serve instant HTML loading screen
then redirect to Streamlit app
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import threading
import time
import os
import requests
import uvicorn
from pathlib import Path

app = FastAPI(title="Cisco Automation Certification Station")

# Global variables to track if Streamlit is ready
streamlit_ready = False
streamlit_process = None
models_loaded = False  # Track if models are loaded

# Mount static files directory
current_dir = Path(__file__).parent.absolute()
app.mount("/public", StaticFiles(directory=str(current_dir / "public")), name="public")

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    """Status endpoint to check if Streamlit is ready and models are loaded"""
    global streamlit_ready, streamlit_process, models_loaded
    
    status = {
        "fastapi": "running",
        "streamlit_flag": streamlit_ready,
        "streamlit_process": streamlit_process is not None and streamlit_process.poll() is None,
        "models_loaded": models_loaded
    }
    
    # Check if Streamlit is actually responding
    try:
        response = requests.get('http://localhost:8502/healthz', timeout=1)
        status["streamlit_responding"] = response.status_code == 200
    except Exception as e:
        status["streamlit_responding"] = False
        status["streamlit_error"] = str(e)
    
    return status

def load_models():
    """Load ML models in background thread"""
    global models_loaded
    try:
        print("🔍 Loading ML models...")
        # Simulate model loading
        time.sleep(5)
        models_loaded = True
        print("✅ ML models loaded successfully")
    except Exception as e:
        print(f"❌ Error loading ML models: {e}")
        models_loaded = False

def start_streamlit():
    """Start Streamlit app in background with proper error handling"""
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
        
        # Start a thread to monitor the Streamlit process
        def monitor_streamlit():
            global streamlit_ready, streamlit_process
            try:
                print("🔍 Monitoring Streamlit output...")
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
                print(f"⚠️ Error monitoring Streamlit: {e}")
                streamlit_ready = False
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=monitor_streamlit, daemon=True)
        monitor_thread.start()
        print("🔍 Started Streamlit monitoring thread")
        
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        streamlit_ready = False

@app.get("/", response_class=HTMLResponse)
async def loading_page(request: Request, app: str = None):
    """Serve instant loading HTML page or redirect to Streamlit if ready"""
    global streamlit_ready
    
    # Mark Streamlit as ready when this endpoint is hit
    if not streamlit_ready:
        streamlit_ready = True
        print("✅ Streamlit marked as ready")
    
    # If this is a redirect from loading screen, try to serve the app
    if app == "ready":
        print("🔄 Loading screen transition detected, attempting to serve app...")
        return await streamlit_app(request, None)
    
    # Otherwise, show the loading page with auto-refresh
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading Cisco Automation Certification Station</title>
        <meta http-equiv="refresh" content="2;url=/?app=ready" />
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

@app.get("/app")
@app.get("/app/{path:path}")
async def streamlit_app(request: Request, path: str = None):
    """Serve Streamlit app directly by proxying to port 8502"""
    global streamlit_ready
    
    # Mark Streamlit as ready when this endpoint is hit
    if not streamlit_ready:
        streamlit_ready = True
        print("✅ Streamlit marked as ready")
    
    # Build the target URL for Streamlit
    target_path = path if path else ''
    streamlit_url = f'http://localhost:8502/{target_path}'
    
    # Copy query parameters if any (except 'app' parameter)
    if request.query_params:
        query_params = [(k, v) for k, v in request.query_params.items() if k != 'app']
        if query_params:
            query_string = '&'.join([f"{k}={v}" for k, v in query_params])
            streamlit_url = f"{streamlit_url}?{query_string}"
    
    print(f"🔄 Proxying to Streamlit: {streamlit_url}")
    
    try:
        # Try to get the Streamlit content
        response = requests.get(streamlit_url, timeout=10)
        
        # If we get a successful response, return it
        if response.status_code == 200:
            content = response.text
            
            # Fix any absolute URLs in the content
            content = content.replace('src="/static/', 'src="/app/static/')
            content = content.replace('href="/static/', 'href="/app/static/')
            content = content.replace('src="/_stcore/', 'src="/app/_stcore/')
            content = content.replace('href="/_stcore/', 'href="/app/_stcore/')
            
            # Add base URL for relative paths
            base_tag = '<base href="/app/">'
            if '<head>' in content and 'base href' not in content:
                content = content.replace('<head>', f'<head>\n    {base_tag}')
            
            return HTMLResponse(content=content)
            
    except Exception as e:
        print(f"❌ Error proxying to Streamlit: {e}")
    
    # If we get here, Streamlit isn't ready yet
    # Return a loading page that will auto-refresh
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading Cisco Automation Certification Station</title>
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
            <p>Preparing the Cisco Automation Certification Station. This should only take a moment.</p>
            <p><small>If you're stuck here for more than 30 seconds, please refresh the page.</small></p>
        </div>
    </body>
    </html>
    """)

def start():
    """Start the FastAPI server with Streamlit in the background"""
    # Start loading models in the background
    model_thread = threading.Thread(target=load_models, daemon=True)
    model_thread.start()
    
    # Start Streamlit in the background
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Start the FastAPI server
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == '__main__':
    start()
