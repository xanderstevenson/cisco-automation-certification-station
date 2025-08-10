#!/usr/bin/env python3
"""
FastAPI application with integrated UI for Cisco Automation Certification Station
"""

import os
import json
import uvicorn
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Cisco Automation Certification Station")

# Set up templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Create static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# In-memory message history (replace with a database in production)
message_history: List[Dict[str, Any]] = []

# HTML template for the main page
MAIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cisco Automation Certification Station</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@1.9.2"></script>
    <style>
        .message-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        @media (max-width: 768px) {
            .message-container {
                width: 100%;
                padding: 0.5rem;
            }
        }
        .typing-indicator {
            display: none;
        }
        .typing-indicator.active {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            color: #666;
        }
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #666;
            border-radius: 50%;
            display: inline-block;
            animation: typing 1.4s infinite ease-in-out;
        }
        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }
        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 0.5rem;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }
        .bot-message {
            background-color: #f5f5f5;
            margin-right: auto;
            border-bottom-left-radius: 0;
        }
        .message-content {
            white-space: pre-wrap;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="flex flex-col min-h-screen">
        <!-- Header -->
        <header class="bg-blue-800 text-white p-4 shadow-md">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-xl font-bold">Cisco Automation Certification Station</h1>
                <div class="flex items-center space-x-4">
                    <a href="#" class="text-white hover:text-blue-200">Home</a>
                    <a href="#" class="text-white hover:text-blue-200">About</a>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-grow container mx-auto p-4">
            <div class="bg-white rounded-lg shadow-lg p-6 mb-4">
                <h2 class="text-2xl font-bold mb-4 text-blue-800">Chat with the Cisco Assistant</h2>
                
                <!-- Messages Container -->
                <div id="messages" class="mb-4 space-y-4" hx-get="/api/messages" hx-trigger="every 1s" hx-swap="innerHTML">
                    <!-- Messages will be loaded here -->
                </div>

                <!-- Typing Indicator -->
                <div id="typing-indicator" class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>

                <!-- Input Form -->
                <form id="message-form" hx-post="/api/message" hx-target="#messages" hx-swap="beforeend" class="mt-4">
                    <div class="flex space-x-2">
                        <input type="text" 
                               name="message" 
                               id="message-input" 
                               placeholder="Ask about Cisco certifications..." 
                               class="flex-grow p-2 border border-gray-300 rounded"
                               required>
                        <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            Send
                        </button>
                    </div>
                </form>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-800 text-white p-4">
            <div class="container mx-auto text-center">
                <p>© 2025 Cisco Automation Certification Station. All rights reserved.</p>
            </div>
        </footer>
    </div>

    <script>
        // Auto-scroll to bottom of messages
        function scrollToBottom() {
            const messages = document.getElementById('messages');
            messages.scrollTop = messages.scrollHeight;
        }

        // Handle form submission
        document.getElementById('message-form').addEventListener('submit', function(e) {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (message) {
                // Show typing indicator
                document.getElementById('typing-indicator').classList.add('active');
                
                // Clear input
                input.value = '';
                
                // Scroll to bottom
                setTimeout(scrollToBottom, 100);
            }
        });

        // Auto-scroll when new messages are loaded
        document.body.addEventListener('htmx:afterSwap', function() {
            scrollToBottom();
            document.getElementById('typing-indicator').classList.remove('active');
        });
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main chat interface"""
    return HTMLResponse(content=MAIN_HTML, status_code=200)

@app.post("/api/message")
async def create_message(message: str = Form(...)):
    """Handle new messages from the user"""
    # Add user message to history
    user_message = {"role": "user", "content": message}
    message_history.append(user_message)
    
    # Here you would typically process the message with your RAG pipeline
    # For now, we'll just echo the message back
    bot_response = {
        "role": "assistant",
        "content": f"You said: {message}\n\nThis is a placeholder response. In a real implementation, this would be generated by the RAG pipeline."
    }
    message_history.append(bot_response)
    
    # Return just the new messages
    return {"messages": [user_message, bot_response]}

@app.get("/api/messages")
async def get_messages():
    """Return all messages"""
    return {"messages": message_history}

# File upload endpoint (example)
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads"""
    try:
        # Save the uploaded file
        file_path = static_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the file (in a real app, you'd do something with it)
        return {"filename": file.filename, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server():
    """Start the FastAPI server"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run("fastapi_ui:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    start_server()
