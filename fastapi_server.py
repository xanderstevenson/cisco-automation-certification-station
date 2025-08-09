#!/usr/bin/env python3
"""
FastAPI server to serve instant HTML loading screen
then redirect to Streamlit app
"""

from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
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
    print("🧠 Loading ML models in background...")
    try:
        # Check if rag directory exists and has required files
        rag_dir = os.path.join(os.path.dirname(__file__), 'rag')
        if not os.path.exists(rag_dir):
            print("⚠️ rag directory not found. Some features may be limited.")
        
        # Try to import and initialize models if possible
        try:
            from rag.retriever import DocumentRetriever
            print("📚 Initializing document retriever...")
            retriever = DocumentRetriever()
            print("✅ Document retriever loaded successfully")
        except ImportError as e:
            print(f"⚠️ Could not load document retriever: {e}")
        except Exception as e:
            print(f"⚠️ Error initializing document retriever: {e}")
        
        # Try to import chat function if available
        try:
            from hybrid_rag_gpt import chat
            print("✅ AI models loaded successfully")
        except ImportError as e:
            print(f"⚠️ Could not load AI models: {e}")
        
        # Set flag to indicate models are loaded (even if some failed)
        models_loaded = True
        print("✅ Model loading completed (some features may be limited)")
        
    except Exception as e:
        print(f"❌ Error in model loading thread: {e}")
        models_loaded = True  # Still set to True to allow the app to run with limited functionality

def start_streamlit():
    """Start Streamlit app in background with proper error handling"""
    global streamlit_ready, streamlit_process
    print("🚀 Starting Streamlit in background thread...")
    try:
        # In Cloud Run, we'll run Streamlit on port 8502 to avoid conflicts
        # and proxy requests through FastAPI
        print("📍 Running Streamlit command...")
        
        # Set environment variables for better error reporting and compatibility
        env = os.environ.copy()
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'
        env['STREAMLIT_SERVER_PORT'] = '8502'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        env['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
        env['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'  # Disable file watching in production
        
        # Add more verbose logging
        print(f"💾 Current directory: {os.getcwd()}")
        print(f"📁 Files in directory: {os.listdir()}")
        print(f"📚 Checking if streamlit_app.py exists: {os.path.exists('streamlit_app.py')}")
        
        # Use absolute path for streamlit_app.py
        streamlit_app_path = os.path.join(os.getcwd(), 'streamlit_app.py')
        print(f"📍 Using absolute path: {streamlit_app_path}")
        
        # Create a custom config.toml file for Streamlit to ensure consistent settings
        config_dir = os.path.join(os.getcwd(), '.streamlit')
        os.makedirs(config_dir, exist_ok=True)
        
        with open(os.path.join(config_dir, 'config.toml'), 'w') as f:
            f.write("""
[server]
# Server settings
headless = true
enableCORS = true
enableXsrfProtection = false
port = 8502
address = "0.0.0.0"

[browser]
# Browser settings
serverAddress = "localhost"
gatherUsageStats = false

[theme]
# Theme settings
base = "light"
            """)
        
        print("📝 Created custom Streamlit config.toml for consistent settings")
        
        # Start Streamlit with the custom config
        streamlit_process = subprocess.Popen([
            "streamlit", "run", streamlit_app_path, 
            "--server.port", "8502",
            "--server.address", "0.0.0.0", 
            "--server.headless", "true",
            "--server.enableCORS", "true",
            "--server.enableXsrfProtection", "false",
            "--browser.serverAddress", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        
        print("🔄 Streamlit process started with PID:", streamlit_process.pid)
        
        # Create a healthz endpoint file for Streamlit
        try:
            healthz_path = os.path.join(os.getcwd(), 'pages')
            os.makedirs(healthz_path, exist_ok=True)
            
            with open(os.path.join(healthz_path, 'healthz.py'), 'w') as f:
                f.write("""
# Health check endpoint for Streamlit
import streamlit as st

# Hide all Streamlit elements
hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp {display: none;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Just return a simple 200 OK
st.write("OK")
                """)
            print("💊 Created Streamlit health check endpoint at /healthz")
        except Exception as e:
            print(f"⚠️ Could not create health check endpoint: {e}")
        
        # Monitor the process for 45 seconds (increased timeout) and capture any errors
        start_time = time.time()
        streamlit_ready = False
        max_wait_time = 45  # seconds
        
        while time.time() - start_time < max_wait_time:
            if streamlit_process.poll() is not None:
                # Process ended - get all output
                stdout, _ = streamlit_process.communicate()
                print(f"❌ Streamlit process ended early!")
                print(f"📊 Exit code: {streamlit_process.returncode}")
                print(f"📝 Full output:\n{stdout}")
                return
            
            # Check if Streamlit is responding on port 8502
            try:
                # Try multiple endpoints to see if Streamlit is ready
                endpoints = ['http://localhost:8502', 'http://localhost:8502/healthz', 'http://0.0.0.0:8502']
                
                for endpoint in endpoints:
                    try:
                        resp = requests.get(endpoint, timeout=2)
                        print(f"🔍 Checking {endpoint}: {resp.status_code}")
                        if resp.status_code == 200:
                            print(f"✅ Streamlit is responding at {endpoint}!")
                            streamlit_ready = True
                            break
                    except Exception as e:
                        print(f"⚠️ {endpoint} not ready: {str(e)[:50]}...")
                
                if streamlit_ready:
                    break
            except Exception as e:
                # Still waiting for Streamlit to start
                print(f"⚠️ Error checking Streamlit status: {str(e)[:50]}...")
                
            time.sleep(1)
            print(f"⏳ Waiting for Streamlit... ({int(time.time() - start_time)}s/{max_wait_time}s)")
        
        if streamlit_process.poll() is None:  # Process still running after monitoring period
            print("✅ Streamlit process is running in background!")
            print("📊 Process PID:", streamlit_process.pid)
            
            # Even if we couldn't connect to Streamlit yet, mark it as ready after the timeout
            # This allows the loading screen to transition to the app page which will continue checking
            if not streamlit_ready:
                print("⚠️ Could not confirm Streamlit is responding, but process is running")
                print("🔄 Setting streamlit_ready=True to allow transition to app page")
                streamlit_ready = True
            
            # Start a thread to continue monitoring the process
            def monitor_streamlit():
                try:
                    # Keep reading output to prevent buffer overflow
                    while streamlit_process.poll() is None:
                        line = streamlit_process.stdout.readline()
                        if line and line.strip():
                            print(f"[Streamlit] {line.strip()}")
                        time.sleep(0.1)
                    # Process ended
                    remaining_output = streamlit_process.stdout.read()
                    if remaining_output:
                        print(f"[Streamlit] {remaining_output}")
                    print(f"⚠️ Streamlit process ended with code: {streamlit_process.returncode}")
                    # Reset the ready flag if the process dies
                    global streamlit_ready
                    streamlit_ready = False
                except Exception as e:
                    print(f"⚠️ Error monitoring Streamlit: {e}")
            
            monitor_thread = threading.Thread(target=monitor_streamlit, daemon=True)
            monitor_thread.start()
            print("🔍 Started Streamlit monitoring thread")
        else:
            stdout, _ = streamlit_process.communicate()
            print(f"❌ Streamlit failed to start!")
            print(f"📊 Exit code: {streamlit_process.returncode}")
            print(f"📝 Output: {stdout}")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")

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
            setTimeout(() => window.location.reload(), 2000);
        </script>
    </body>
    </html>
    """)
    
    # Add retry logic for the health check
    max_retries = 20  # Increased from 10 to 20
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Check if Streamlit is responding
            health_check = requests.get('http://localhost:8502/healthz', timeout=1)
            if health_check.status_code == 200 and health_check.text.strip() == "OK":
                print(" Streamlit is ready!")
                break
        except Exception as e:
            print(f" Streamlit not ready yet (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
            
            if attempt == max_retries - 1:
                return HTMLResponse(content=f"""
                    <html>
                    <head><title>Loading...</title></head>
                    <body>
                        <h2>Application is still starting up...</h2>
                        <p>This is taking longer than expected. Please wait or try refreshing the page.</p>
                        <p><a href="/app?app=ready">Click here to try again</a></p>
                        <script>
                            setTimeout(function() {{
                                window.location.href = "/app?app=ready";
                            }}, 2000);
                        </script>
                    </body>
                    </html>
                """, status_code=503)
                
            time.sleep(retry_delay)
    
    try:
        # Forward the request to Streamlit
        streamlit_response = requests.get(streamlit_url, timeout=10)
        
        # For static files, return them directly
        if path and any(ext in path for ext in ['.js', '.css', '.woff2', '.png', '.jpg', '.jpeg', '.gif', '.ico']):
            return Response(
                content=streamlit_response.content,
                media_type=streamlit_response.headers.get('content-type')
            )
        
        # For HTML content, process it
        if 'text/html' in streamlit_response.headers.get('content-type', ''):
            content = streamlit_response.text
            # Fix any absolute URLs that might point to localhost:8502
            content = content.replace('http://localhost:8502', '')
            # Add base URL for static files
            content = content.replace('src="/static/', 'src="/app/static/')
            content = content.replace('href="/static/', 'href="/app/static/')
            return HTMLResponse(content=content)
            
        return Response(
            content=streamlit_response.content,
            media_type=streamlit_response.headers.get('content-type')
        )
        
    except Exception as e:
        print(f" Error proxying to Streamlit: {e}")
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Error</title></head>
            <body>
                <h2>Error loading the application</h2>
                <p>We're having trouble connecting to the application server.</p>
                <p><a href="/">Click here to return to the home page</a></p>
                <script>
                    setTimeout(function() {{
                        window.location.href = "/";
                    }}, 5000);
                </script>
            </body>
            </html>
            """,
            status_code=502
        )
    
    try:
        # Forward the request to Streamlit
        streamlit_response = requests.get(streamlit_url, timeout=10)
        
        # For static files, return them directly
        if path and any(ext in path for ext in ['.js', '.css', '.woff2', '.png', '.jpg', '.jpeg', '.gif', '.ico']):
            return Response(
                content=streamlit_response.content,
                media_type=streamlit_response.headers.get('content-type')
            )
        
        # For HTML content, process it
        if 'text/html' in streamlit_response.headers.get('content-type', ''):
            content = streamlit_response.text
            # Fix any absolute URLs that might point to localhost:8502
            content = content.replace('http://localhost:8502', '')
            # Add base URL for static files
            content = content.replace('src="/static/', 'src="/app/static/')
            content = content.replace('href="/static/', 'href="/app/static/')
            content = content.replace('src="/_stcore/', 'src="/app/_stcore/')
            content = content.replace('href="/_stcore/', 'href="/app/_stcore/')
            
            # Add base tag to ensure relative URLs work
            base_tag = '<base href="/app/">'
            if '<head>' in content and 'base href' not in content:
                content = content.replace('<head>', f'<head>\n    {base_tag}')
            
            return HTMLResponse(content=content)
        
        # For other content types, return as-is
        return Response(
            content=streamlit_response.content,
            media_type=streamlit_response.headers.get('content-type')
        )
        
    except Exception as proxy_error:
        print(f"❌ Error proxying Streamlit content: {proxy_error}")
        
        # Return a simple error page with a refresh button
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error Loading Application</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error-container { max-width: 600px; margin: 0 auto; }
                .btn { 
                    background-color: #1BA0D7; 
                    color: white; 
                    border: none; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                            margin-top: 20px;
                        }
                        .btn:hover { background-color: #0D5F8A; }
                    </style>
        </head>
        <body>
            <div class="error-container">
                <h2>Error Loading Application</h2>
                <p>We're having trouble loading the application. The server might still be starting up.</p>
                <p>Error details: {error}</p>
                <a href="/app" class="btn">Try Again</a>
            </div>
        </body>
        </html>
        """.format(error=str(proxy_error))
        
        return HTMLResponse(content=error_html, status_code=500)
    
    except Exception as e:
        print(f"❌ Error in streamlit_app: {e}")
        return HTMLResponse(content=f'''
        <html>
        <head>
            <title>Error</title>
            <meta http-equiv="refresh" content="5;url=/app" />
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>Error connecting to Streamlit</h2>
            <p>Error details: {str(e)[:200]}</p>
            <p>Automatically retrying in 5 seconds...</p>
            <p><a href="/app">Try again now</a></p>
        </body>
        </html>
        ''', status_code=500)
        
    except Exception as e:
        print(f"❌ Streamlit not ready yet: {e}")
        # Return a simple message while Streamlit loads with auto-refresh
        return HTMLResponse(content=f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Loading Cisco Automation Certification Station...</title>
            <meta http-equiv="refresh" content="3;url=/app" />
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    margin: 0;
                    background: #f5f5f5;
                }}
                .loading-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .loader {{ 
                    border: 8px solid #f3f3f3;
                    border-top: 8px solid #0D6EFD;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    animation: spin 2s linear infinite;
                    margin: 0 auto 20px;
                }}
                @keyframes spin {{ 
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                h1, h2, h3 {{ color: #333; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="loading-container">
                <div class="loader"></div>
                <h2>Loading Cisco Automation Certification Station</h2>
                <p>This may take a moment as we prepare your environment...</p>
                <p><small>Status: {str(e)[:100]}</small></p>
            </div>
        </body>
        </html>
        ''')

def start():
    # Start model loading in background thread
    models_thread = threading.Thread(target=load_models, daemon=True)
    models_thread.start()
    print("🧠 Started model loading in background thread")
    
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    print("🚀 Started Streamlit in background thread")
    
    # Try multiple ports if needed
    ports_to_try = [8000, 9000, 9001, 9002, 9003, 9004, 9005]
    
    for port in ports_to_try:
        try:
            print(f"🌐 Attempting to start FastAPI server on port {port}...")
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=port,
                log_level="info",
                timeout_keep_alive=120
            )
            server = uvicorn.Server(config)
            print(f"✅ Successfully started FastAPI server on port {port}")
            server.run()
            break  # Exit the loop if server starts successfully
        except OSError as e:
            if "address already in use" in str(e):
                print(f"⚠️  Port {port} is already in use, trying next port...")
                if port == ports_to_try[-1]:
                    print("❌ All ports are in use. Please close applications using these ports:")
                    print(f"    - {', '.join(map(str, ports_to_try))}")
                    return
                continue
            else:
                print(f"❌ Error starting server: {e}")
                return

if __name__ == '__main__':
    start()
