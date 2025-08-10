#!/usr/bin/env python3
"""
Minimal test of FastAPI with Streamlit UI
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import asyncio
import subprocess
import threading

app = FastAPI()

# Simple HTML response for the root URL
@app.get("/")
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading Test</title>
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
        </style>
        <script>
            // Redirect to /app after 2 seconds
            setTimeout(function() {
                window.location.href = "/app";
            }, 2000);
        </script>
    </head>
    <body>
        <div class="loading-container">
            <div class="spinner"></div>
            <h2>Loading Test Page</h2>
            <p>Redirecting to Streamlit app...</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Simple Streamlit app
@app.get("/app")
async def streamlit_app():
    # Very minimal Streamlit app
    import streamlit as st
    
    st.set_page_config(
        page_title="Test Streamlit App",
        page_icon="🔌",
        layout="wide"
    )
    
    st.title("Test Streamlit App")
    st.write("Hello from Streamlit!")
    
    return Response(content="Streamlit app loaded", media_type="text/plain")

def start_server():
    """Start the FastAPI server"""
    uvicorn.run("minimal_test:app", host="0.0.0.0", port=8080, log_level="info")

if __name__ == "__main__":
    start_server()
