#!/usr/bin/env python3
"""
Simplified FastAPI-only version for testing
Uses mock responses to test the UI/UX without heavy ML dependencies
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time
from pathlib import Path

app = FastAPI(title="Cisco Automation Certification Station")

# Mount static files directory
current_dir = Path(__file__).parent.absolute()
app.mount("/public", StaticFiles(directory=str(current_dir / "public")), name="public")

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    """Status endpoint - always ready for testing"""
    return {
        "status": "ok",
        "streamlit_flag": True,
        "streamlit_ready": True,
        "models_loaded": True
    }

@app.get("/", response_class=HTMLResponse)
async def loading_page(request: Request, app: str = None):
    """Serve custom loading HTML page or redirect to app if ready"""
    
    # If this is a redirect from loading screen, serve the main app
    if app == "ready":
        print("🔄 Loading screen transition detected, serving main app...")
        return await main_app()
    
    # Otherwise, serve the custom loading page
    loading_path = current_dir / "loading.html"
    print(f"🔍 Reading loading.html from: {loading_path}")
    
    try:
        with open(loading_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Successfully read loading.html ({len(content)} chars)")
        return HTMLResponse(content=content)
    except Exception as e:
        print(f"❌ Error reading loading.html: {e}")
        return HTMLResponse(content=f"Error loading page: {e}", status_code=500)

@app.get("/app", response_class=HTMLResponse)
async def main_app():
    """Serve the main application - simplified version"""
    
    # Read the Cisco logo and encode as base64
    logo_path = current_dir / "public" / "Cisco-automation-certification-station.png"
    logo_base64 = ""
    if logo_path.exists():
        import base64
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
            logo_base64 = f"data:image/png;base64,{logo_data}"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Automation Certification Station</title>
    <style>
        /* Cisco Blue Color Palette */
        :root {{
            --cisco-blue: #1BA0D7;
            --cisco-dark-blue: #0D5F8A;
            --cisco-light-blue: #5CB3D9;
        }}

        body, html {{
            background-color: white !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            color: #000000;
        }}

        .main-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
        }}

        .cisco-logo-container {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .cisco-logo-container img {{
            max-width: 100%;
            height: auto;
        }}

        .learn-cisco-heading {{
            text-align: center;
            margin-top: -1.5rem;
            margin-bottom: 1rem;
            font-size: 18px;
        }}

        .learn-cisco-heading a {{
            color: #1BA0D7;
            text-decoration: none;
            font-weight: 600;
        }}

        .chat-title {{
            text-align: center;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}

        .chat-form {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .chat-input {{
            flex: 1;
            padding: 12px;
            border: 2px solid var(--cisco-blue);
            border-radius: 5px;
            font-size: 16px;
            background-color: white;
            color: #000000;
        }}

        .chat-button {{
            background-color: var(--cisco-light-blue);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 12px 20px;
            font-weight: 600;
            cursor: pointer;
            font-size: 16px;
        }}

        .chat-button:hover {{
            background-color: var(--cisco-blue);
        }}

        .chat-message {{
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            border-left: 4px solid var(--cisco-blue);
        }}

        .user-message {{
            background-color: #f0f8ff;
            margin-left: 2rem;
            color: #333;
        }}

        .bot-message {{
            background-color: #f9f9f9;
            margin-right: 2rem;
            color: #333;
            line-height: 1.6;
        }}

        .loading-spinner {{
            display: none;
            text-align: center;
            padding: 20px;
        }}

        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--cisco-blue);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .welcome-content {{
            margin-top: 20px;
            line-height: 1.6;
        }}

        .welcome-content a {{
            color: var(--cisco-blue);
            text-decoration: none;
        }}

        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Logo -->
        <div class="cisco-logo-container">
            {f'<img src="{logo_base64}" alt="Cisco Automation Certification Station">' if logo_base64 else '<h3>🏅 Cisco Automation Certification Station</h3>'}
        </div>

        <!-- Learn with Cisco heading -->
        <div class="learn-cisco-heading">
            <a href="https://www.cisco.com/site/us/en/learn/training-certifications/index.html" target="_blank">Learn with Cisco</a>
        </div>

        <!-- Chat title -->
        <div class="chat-title">
            <h5>Ask about Cisco automation certifications, exam preparation, or technical topics:</h5>
        </div>

        <!-- Chat form -->
        <form class="chat-form" id="chatForm">
            <input 
                type="text" 
                class="chat-input" 
                id="chatInput" 
                placeholder="Type your question here..."
                required
            >
            <button type="submit" class="chat-button" id="sendButton">Send</button>
        </form>

        <!-- Loading spinner -->
        <div class="loading-spinner" id="loadingSpinner">
            <div class="spinner"></div>
            <p>⚡ Searching Cisco resources and generating a comprehensive response...</p>
        </div>

        <!-- Chat messages -->
        <div class="chat-messages" id="chatMessages"></div>

        <!-- Welcome content -->
        <div class="welcome-content">
            <p><strong>🎉 FastAPI Version Working!</strong></p>
            <p>This is the FastAPI-only version with identical UX/UI to the Streamlit version. The custom loading page transitioned perfectly!</p>
            
            <h4>What's Different:</h4>
            <ul>
                <li>✅ Same beautiful custom loading page</li>
                <li>✅ Same Cisco branding and design</li>
                <li>✅ Same responsive layout</li>
                <li>✅ Much faster and simpler for Cloud Run</li>
                <li>✅ No Streamlit complexity</li>
            </ul>

            <p>Try sending a message above to test the chat interface!</p>
        </div>

        <!-- Footer -->
        <div class="footer">
            FastAPI Version | Built with ❤️ for Cisco Certification Communities
        </div>
    </div>

    <script>
        const chatForm = document.getElementById('chatForm');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const chatMessages = document.getElementById('chatMessages');

        chatForm.addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const userInput = chatInput.value.trim();
            if (!userInput) return;

            // Clear input and disable form
            chatInput.value = '';
            sendButton.disabled = true;
            
            // Add user message
            addMessage(userInput, 'user');
            
            // Show loading
            loadingSpinner.style.display = 'block';
            
            try {{
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const mockResponse = `Thank you for asking about "${{userInput}}"! 

**This is a mock response demonstrating the FastAPI version.** In the real implementation, this would connect to your hybrid_rag_gpt system.

Key points about your question:
- ✅ The FastAPI interface is working perfectly
- ✅ The transition from loading page was seamless  
- ✅ All styling and functionality matches the original
- 🚀 Ready for Google Cloud Run deployment!

Try asking about CCNA Automation, DevNet certifications, or NETCONF vs RESTCONF!`;
                
                addMessage(mockResponse, 'bot');
                
            }} catch (error) {{
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }} finally {{
                loadingSpinner.style.display = 'none';
                sendButton.disabled = false;
                chatInput.focus();
            }}
        }});

        function addMessage(content, type) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${{type}}-message`;
            
            if (type === 'user') {{
                messageDiv.innerHTML = `<strong>You:</strong> ${{escapeHtml(content)}}`;
            }} else {{
                messageDiv.innerHTML = `<strong>Cisco Expert:</strong><br/><br/>${{formatResponse(content)}}`;
            }}
            
            chatMessages.appendChild(messageDiv);
            messageDiv.scrollIntoView({{ behavior: 'smooth' }});
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function formatResponse(text) {{
            return text
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\n/g, '<br/>')
                .replace(/(https?:\\/\\/[^\\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        }}

        // Focus on input when page loads
        chatInput.focus();
    </script>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

@app.post("/chat")
async def chat_endpoint(request: Request):
    """Mock chat endpoint for testing"""
    data = await request.json()
    user_message = data.get("message", "")
    
    # Simulate processing time
    await asyncio.sleep(1)
    
    mock_response = f"""Thank you for your question about "{user_message}"!

This is a **mock response** from the simplified FastAPI version. In the full implementation, this would connect to your hybrid_rag_gpt system for real AI responses.

**Key FastAPI advantages:**
- ⚡ Much faster startup than Streamlit
- 🌐 Better Cloud Run compatibility  
- 💾 Lower memory usage
- 🔧 Simpler deployment

The UI/UX is identical to your Streamlit version!"""
    
    return JSONResponse(content={"response": mock_response})

if __name__ == "__main__":
    import uvicorn
    import asyncio
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting simplified FastAPI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
