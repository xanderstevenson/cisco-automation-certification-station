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
    """Start Streamlit app in background"""
    global streamlit_ready
    try:
        # Start Streamlit on port 8502
        subprocess.run([
            "streamlit", "run", "streamlit_app.py", 
            "--server.port", "8502",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
        streamlit_ready = True
    except Exception as e:
        print(f"Error starting Streamlit: {e}")

@app.route('/')
def loading_page():
    """Serve instant loading HTML page"""
    return send_file('loading.html')

@app.route('/app')
def streamlit_app():
    """Redirect to Streamlit app"""
    return redirect('http://localhost:8502')

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
