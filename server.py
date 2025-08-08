#!/usr/bin/env python3
"""
Simple Flask server to serve instant HTML loading screen
then redirect to Streamlit app
"""

from flask import Flask, send_file, redirect
import subprocess
import threading
import time
import os

app = Flask(__name__)

# Global variable to track if Streamlit is ready
streamlit_ready = False

def start_streamlit():
    """Start Streamlit app in background with proper error handling"""
    global streamlit_ready
    print("🚀 Starting Streamlit in background thread...")
    try:
        # Start Streamlit on port 8502 with detailed logging
        print("📡 Running Streamlit command...")
        
        import os
        # Set environment variables for better error reporting
        env = os.environ.copy()
        env['STREAMLIT_SERVER_HEADLESS'] = 'true'
        env['STREAMLIT_SERVER_PORT'] = '8502'
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        result = subprocess.Popen([
            "streamlit", "run", "streamlit_app.py", 
            "--server.port", "8502",
            "--server.address", "0.0.0.0", 
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        
        print("🔄 Streamlit process started, monitoring output...")
        
        # Monitor the process for 10 seconds and capture any errors
        import time
        start_time = time.time()
        while time.time() - start_time < 10:
            if result.poll() is not None:
                # Process ended - get all output
                stdout, _ = result.communicate()
                print(f"❌ Streamlit process ended early!")
                print(f"📊 Exit code: {result.returncode}")
                print(f"📝 Full output:\n{stdout}")
                return
            time.sleep(1)
        
        if result.poll() is None:  # Process still running after 10 seconds
            print("✅ Streamlit process is running in background!")
            print("📊 Process PID:", result.pid)
            streamlit_ready = True
            
            # Start a thread to continue monitoring the process
            import threading
            def monitor_streamlit():
                try:
                    # Keep reading output to prevent buffer overflow
                    while result.poll() is None:
                        line = result.stdout.readline()
                        if line.strip():
                            print(f"[Streamlit] {line.strip()}")
                        time.sleep(0.1)
                    # Process ended
                    remaining_output = result.stdout.read()
                    if remaining_output:
                        print(f"[Streamlit] {remaining_output}")
                    print(f"⚠️ Streamlit process ended with code: {result.returncode}")
                except Exception as e:
                    print(f"⚠️ Error monitoring Streamlit: {e}")
            
            threading.Thread(target=monitor_streamlit, daemon=True).start()
        else:
            stdout, _ = result.communicate()
            print(f"❌ Streamlit failed to start!")
            print(f"📊 Exit code: {result.returncode}")
            print(f"📝 Output: {stdout}")
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")

@app.route('/')
def loading_page():
    """Serve instant loading HTML page or redirect to Streamlit if ready"""
    from flask import request
    
    # Check if this is a redirect from loading screen
    if request.args.get('app') == 'ready':
        print("🔄 Loading screen transition detected, redirecting to /app...")
        return redirect('/app')
    
    # Otherwise serve loading screen
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    loading_path = os.path.join(current_dir, 'loading.html')
    print(f"🔍 Reading loading.html content from: {loading_path}")
    
    try:
        with open(loading_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Successfully read loading.html ({len(content)} chars)")
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        print(f"❌ Error reading loading.html: {e}")
        return f"Error loading page: {e}", 500

@app.route('/app')
def streamlit_app():
    """Serve Streamlit app directly by proxying to port 8502"""
    import requests
    try:
        # Check if Streamlit is ready
        response = requests.get('http://localhost:8502', timeout=5)
        print(f"✅ Streamlit is ready! Status: {response.status_code}")
        
        # Streamlit is ready - redirect to it running on same Cloud Run instance
        from flask import request
        base_url = request.host_url.rstrip('/')
        streamlit_url = f"{base_url}:8502"
        print(f"🎯 Redirecting to Streamlit at: {streamlit_url}")
        return redirect(streamlit_url)
        
    except Exception as e:
        print(f"❌ Streamlit not ready yet: {e}")
        # Return a simple message while Streamlit loads
        return '''
        <html>
        <head><title>Loading...</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>Streamlit app is starting...</h2>
            <p>Please wait a moment and <a href="/app">try again</a></p>
            <script>setTimeout(() => window.location.reload(), 5000);</script>
        </body>
        </html>
        ''', 200

@app.route('/public/<path:filename>')
def serve_static(filename):
    """Serve static files for loading page"""
    return send_file(f'public/{filename}')

if __name__ == '__main__':
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Start Flask server on main port
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
