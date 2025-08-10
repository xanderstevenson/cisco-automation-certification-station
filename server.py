#!/usr/bin/env python3
"""
Simple Flask server to serve instant HTML loading screen
then redirect to Streamlit app
"""

from flask import Flask, send_file, redirect, jsonify
import subprocess
import threading
import time
import os

app = Flask(__name__, static_folder=None)

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
@app.route('/app/<path:subpath>')
def streamlit_app(subpath=None):
    """Serve Streamlit app directly by proxying to port 8502 with full Cloud Run support"""
    import requests
    from flask import request
    
    try:
        # Build the full URL for the Streamlit backend
        streamlit_base_url = 'http://localhost:8502'
        if subpath:
            streamlit_url = f"{streamlit_base_url}/{subpath}"
        else:
            streamlit_url = streamlit_base_url
        
        # Add query parameters if they exist
        if request.query_string:
            streamlit_url += f"?{request.query_string.decode()}"
        
        print(f"🔗 Proxying request to: {streamlit_url}")
        
        # Forward the request to Streamlit with proper headers
        headers = {key: value for key, value in request.headers if key.lower() not in ['host']}
        
        if request.method == 'GET':
            streamlit_response = requests.get(
                streamlit_url, 
                headers=headers,
                timeout=10,
                allow_redirects=False
            )
        elif request.method == 'POST':
            streamlit_response = requests.post(
                streamlit_url,
                headers=headers,
                data=request.get_data(),
                timeout=10,
                allow_redirects=False
            )
        else:
            # Handle other HTTP methods
            streamlit_response = requests.request(
                request.method,
                streamlit_url,
                headers=headers,
                data=request.get_data(),
                timeout=10,
                allow_redirects=False
            )
        
        print(f"✅ Streamlit responded with status: {streamlit_response.status_code}")
        
        # Handle different content types properly
        content_type = streamlit_response.headers.get('content-type', 'text/html')
        
        # For HTML content, fix any localhost references
        if 'text/html' in content_type:
            content = streamlit_response.text
            # Fix relative paths to absolute paths so our Flask routes can handle them
            content = content.replace('href="./favicon.png"', 'href="/favicon.png"')
            content = content.replace('href="./static/', 'href="/static/')
            content = content.replace('src="./static/', 'src="/static/')
            
            # Also fix any image paths that might be relative
            content = content.replace('src="./public/', 'src="/public/')
            content = content.replace('href="./public/', 'href="/public/')
            
            # Fix any media or asset paths
            content = content.replace('src="./media/', 'src="/media/')
            content = content.replace('href="./media/', 'href="/media/')
            
            # Debug: Log the modified content
            print(f"🔍 Modified HTML content length: {len(content)}")
            print(f"🔍 Content preview: {content[:500]}...")
            
            return content, streamlit_response.status_code, {
                'Content-Type': content_type
            }
        else:
            # For non-HTML content (CSS, JS, images), return as-is
            return streamlit_response.content, streamlit_response.status_code, {
                'Content-Type': content_type
            }
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Streamlit - it may not be started yet")
        return '''
        <html>
        <head>
            <title>Starting Application...</title>
            <meta http-equiv="refresh" content="5;url=/app" />
            <style>
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: #f8f9fa;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #1BA0D7;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner"></div>
                <h2>🚀 Starting Cisco Automation Certification Station</h2>
                <p>The application is initializing. This may take a moment on first load.</p>
                <p><small>Refreshing automatically in 5 seconds...</small></p>
            </div>
            <script>
                setTimeout(() => window.location.reload(), 5000);
            </script>
        </body>
        </html>
        ''', 503
        
    except requests.exceptions.Timeout:
        print("⏰ Streamlit request timed out")
        return '''
        <html>
        <head>
            <title>Loading...</title>
            <meta http-equiv="refresh" content="3;url=/app" />
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>⏰ Application is loading...</h2>
            <p>The request is taking longer than expected. Retrying...</p>
            <script>setTimeout(() => window.location.reload(), 3000);</script>
        </body>
        </html>
        ''', 504
        
    except Exception as e:
        print(f"❌ Unexpected error proxying to Streamlit: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        return '''
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>⚠️ Temporary Error</h2>
            <p>We're experiencing a temporary issue. Please try again.</p>
            <p><a href="/app" style="color: #1BA0D7;">🔄 Retry</a> | <a href="/" style="color: #1BA0D7;">🏠 Home</a></p>
            <script>setTimeout(() => window.location.href = '/app', 5000);</script>
        </body>
        </html>
        ''', 500

@app.route('/debug/streamlit')
def debug_streamlit():
    """Debug endpoint to check what Streamlit is serving"""
    import requests
    try:
        # Try to get the main Streamlit page and see what static files it references
        response = requests.get('http://localhost:8502', timeout=5)
        
        if response.status_code == 200:
            content = response.text
            # Extract ALL file references with broader patterns
            import re
            
            # Look for all href and src attributes
            all_hrefs = re.findall(r'href="([^"]+)"', content)
            all_srcs = re.findall(r'src="([^"]+)"', content)
            
            # More specific patterns
            css_files = re.findall(r'href="([^"]*\.css[^"]*)"', content)
            js_files = re.findall(r'src="([^"]*\.js[^"]*)"', content)
            font_files = re.findall(r'([^"]*\.(woff2?|ttf|eot)[^"]*)', content)
            
            # Look for _stcore references
            stcore_refs = re.findall(r'(/_stcore/[^"]+)', content)
            
            debug_info = {
                "streamlit_status": response.status_code,
                "all_hrefs": all_hrefs,
                "all_srcs": all_srcs,
                "css_files": css_files,
                "js_files": js_files, 
                "font_files": font_files,
                "stcore_refs": stcore_refs,
                "full_content": content  # Show full content to see what's actually there
            }
            
            from flask import jsonify
            return jsonify(debug_info)
        else:
            return f"Streamlit not responding: {response.status_code}", 500
            
    except Exception as e:
        from flask import jsonify
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status_check():
    """Status endpoint to check if Streamlit is ready and models are loaded"""
    global streamlit_ready
    
    # Check if Streamlit is actually responding
    import requests
    from flask import jsonify
    
    streamlit_responsive = False
    models_loaded = False
    
    try:
        response = requests.get('http://localhost:8502/healthz', timeout=1)
        if response.status_code == 200 and response.text.strip() == "OK":
            streamlit_responsive = True
            models_loaded = True  # Assume models are loaded if Streamlit is responding
    except:
        streamlit_responsive = False
    
    return jsonify({
        "status": "ok",
        "streamlit_ready": streamlit_responsive,
        "streamlit_flag": streamlit_responsive,
        "models_loaded": models_loaded
    })

@app.route('/healthz')
def health_check():
    """Health check endpoint for Cloud Run"""
    from flask import jsonify
    return jsonify({"status": "ok"})

@app.route('/test-static')
def test_static_route():
    """Test route to verify Flask routing is working"""
    print("🔍 Test static route called!")
    return "Static route test working"

@app.route('/static/<path:filename>')
def serve_streamlit_static(filename):
    """Proxy Streamlit static files"""
    print(f"🎯 STATIC ROUTE CALLED with filename: {filename}")
    import requests
    try:
        # Try with leading slash first
        static_url = f'http://localhost:8502/static/{filename}'
        print(f"🔍 Trying to fetch static file: {static_url}")
        
        response = requests.get(static_url, timeout=5)
        print(f"📊 Static file response: {response.status_code} for {filename}")
        
        if response.status_code == 200:
            print(f"✅ Successfully served static file: {filename}")
            return response.content, response.status_code, {
                'Content-Type': response.headers.get('content-type', 'application/octet-stream')
            }
        else:
            # Try without the leading slash - maybe Streamlit serves them differently
            alt_url = f'http://localhost:8502/{filename}'
            print(f"🔍 Trying alternative URL: {alt_url}")
            alt_response = requests.get(alt_url, timeout=5)
            print(f"📊 Alternative response: {alt_response.status_code}")
            
            if alt_response.status_code == 200:
                print(f"✅ Successfully served via alternative URL: {filename}")
                return alt_response.content, alt_response.status_code, {
                    'Content-Type': alt_response.headers.get('content-type', 'application/octet-stream')
                }
            
            print(f"❌ Static file not found on Streamlit server: {filename}")
            print(f"❌ Tried both: {static_url} and {alt_url}")
            return "File not found", 404
            
    except Exception as e:
        print(f"❌ Error serving static file {filename}: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return "File not found", 404

@app.route('/_stcore/<path:filename>')
def serve_streamlit_core(filename):
    """Proxy Streamlit core files"""
    import requests
    from flask import request
    
    try:
        # Build the URL with query parameters
        core_url = f'http://localhost:8502/_stcore/{filename}'
        if request.query_string:
            core_url += f"?{request.query_string.decode()}"
            
        print(f"🔍 Trying to fetch core file: {core_url}")
        
        # Forward headers (excluding host)
        headers = {key: value for key, value in request.headers if key.lower() not in ['host']}
        
        # Handle different HTTP methods
        if request.method == 'GET':
            response = requests.get(core_url, headers=headers, timeout=5)
        elif request.method == 'POST':
            response = requests.post(core_url, headers=headers, data=request.get_data(), timeout=5)
        else:
            response = requests.request(request.method, core_url, headers=headers, data=request.get_data(), timeout=5)
            
        print(f"📊 Core file response: {response.status_code} for {filename}")
        
        return response.content, response.status_code, {
            'Content-Type': response.headers.get('content-type', 'application/octet-stream')
        }
    except Exception as e:
        print(f"❌ Error serving core file {filename}: {e}")
        return "File not found", 404

@app.route('/favicon.png')
@app.route('/favicon.ico')
def serve_favicon():
    """Serve favicon from Streamlit or fallback"""
    import requests
    try:
        # Try to get favicon from Streamlit
        response = requests.get('http://localhost:8502/favicon.png', timeout=2)
        if response.status_code == 200:
            return response.content, 200, {'Content-Type': 'image/png'}
    except:
        pass
    
    # Fallback to our own favicon if available
    try:
        return send_file('public/Cisco-automation-certification-station.png')
    except:
        return "No favicon", 404

@app.route('/media/<path:filename>')
def serve_streamlit_media(filename):
    """Proxy Streamlit media files"""
    print(f"🎯 MEDIA ROUTE CALLED with filename: {filename}")
    import requests
    try:
        media_url = f'http://localhost:8502/media/{filename}'
        print(f"🔍 Trying to fetch media file: {media_url}")
        
        response = requests.get(media_url, timeout=5)
        print(f"📊 Media file response: {response.status_code} for {filename}")
        
        if response.status_code == 200:
            print(f"✅ Successfully served media file: {filename}")
            return response.content, response.status_code, {
                'Content-Type': response.headers.get('content-type', 'application/octet-stream')
            }
        else:
            print(f"❌ Media file not found on Streamlit server: {filename}")
            return "File not found", 404
            
    except Exception as e:
        print(f"❌ Error serving media file {filename}: {e}")
        return "File not found", 404

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
