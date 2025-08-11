#!/usr/bin/env python3
"""
FastAPI-only version of Cisco Automation Certification Station
Maintains exact same UX/UI as Streamlit version but eliminates complexity
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import threading
import time
from pathlib import Path
from hybrid_rag_gpt import chat

app = FastAPI(title="Cisco Automation Certification Station")

# Global variables
models_loaded = False
app_ready = False

# Mount static files directory
current_dir = Path(__file__).parent.absolute()
app.mount("/public", StaticFiles(directory=str(current_dir / "public")), name="public")

def load_models():
    """Load ML models in background thread"""
    global models_loaded
    try:
        print("🔍 Loading ML models...")
        # Preload the chat function and models
        from hybrid_rag_gpt import load_vector_store
        load_vector_store()
        models_loaded = True
        print("✅ ML models loaded successfully")
    except Exception as e:
        print(f"❌ Error loading ML models: {e}")
        models_loaded = False

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    # Start model loading in background
    threading.Thread(target=load_models, daemon=True).start()
    print("🚀 FastAPI startup complete, loading models in background...")

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    """Status endpoint to check if models are loaded"""
    global models_loaded
    
    return {
        "status": "ok",
        "streamlit_flag": models_loaded,  # Keep same API for loading page compatibility
        "streamlit_ready": models_loaded,
        "models_loaded": models_loaded
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
    """Serve the main application - identical to Streamlit version"""
    
    # Read the Cisco logo and encode as base64
    logo_path = current_dir / "public" / "Cisco-automation-certification-station.png"
    logo_base64 = ""
    if logo_path.exists():
        import base64
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
            logo_base64 = f"data:image/png;base64,{logo_data}"
    
    # Read the certification badges image
    cert_image_path = current_dir / "public" / "Automation_Cert_badges_Current_Future.png"
    cert_image_base64 = ""
    if cert_image_path.exists():
        import base64
        with open(cert_image_path, "rb") as f:
            cert_data = base64.b64encode(f.read()).decode()
            cert_image_base64 = f"data:image/png;base64,{cert_data}"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cisco Automation Certification Station</title>
    <link rel="icon" href="/public/Cisco-automation-certification-station.png" type="image/png">
    <style>
        /* Cisco Blue Color Palette */
        :root {{
            --cisco-blue: #1BA0D7;
            --cisco-dark-blue: #0D5F8A;
            --cisco-light-blue: #5CB3D9;
        }}

        /* Force white background for entire app */
        body, html {{
            background-color: white !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            color: #000000;
        }}

        /* Main container */
        .main-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            position: relative;  /* Ensure proper stacking context */
            left: 0;  /* Reset any offset */
            transform: none;  /* Reset any transforms */
        }}

        /* Logo container */
        .cisco-logo-container {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .cisco-logo-container img {{
            max-width: 100%;
            height: auto;
        }}

        /* Learn with Cisco heading */
        .learn-cisco-heading {{
            text-align: center;
            margin-top: 0.5rem; /* add extra spacing from logo */
            margin-bottom: 1rem;
            font-size: 18px;
        }}

        .learn-cisco-heading a {{
            color: #1BA0D7;
            text-decoration: none;
            font-weight: 600;
        }}

        .learn-cisco-heading a:hover {{
            text-decoration: underline;
        }}

        /* Chat interface */
        .chat-title {{
            text-align: center;
            margin-bottom: 1rem;
            font-size: 1.3rem; /* increased by 2px */
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

        .chat-input:focus {{
            outline: none;
            border-color: var(--cisco-dark-blue);
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

        .chat-button:disabled {{
            background-color: #ccc;
            cursor: not-allowed;
        }}

        /* Chat messages */
        .chat-messages {{
            margin-bottom: 20px;
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

        .bot-message strong {{
            color: var(--cisco-blue);
            display: block;
            margin-bottom: 0.5rem;
        }}

        /* Loading spinner */
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

        /* Welcome content */
        .welcome-content {{
            margin-top: 20px;
            line-height: 1.6;
        }}

        .welcome-content h4 {{
            color: var(--cisco-dark-blue);
            margin-top: 1.5rem;
        }}

        .welcome-content a {{
            color: var(--cisco-blue);
            text-decoration: none;
        }}

        .welcome-content a:hover {{
            text-decoration: underline;
        }}

        /* Certification image */
        .cert-image {{
            text-align: center;
            margin: 20px 0;
        }}

        .cert-image img {{
            max-width: 100%;
            height: auto;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}

        .footer a {{
            color: var(--cisco-blue);
            text-decoration: none;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        /* Responsive design */
        @media (max-width: 768px) {{
            .main-container {{
                padding: 10px;
            }}
            
            .chat-form {{
                flex-direction: column;
            }}
            
            .user-message {{
                margin-left: 0;
            }}
            
            .bot-message {{
                margin-right: 0;
            }}
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
            <p>Welcome to your AI-powered Cisco automation certification advisor. I'm here to help you improve your knowledge in and skills with Cisco network automation technologies and prepare you for certifications including:</p>

            <ul>
                <li><a href="https://learningnetwork.cisco.com/s/ccnaauto-exam-topics" target="_blank">CCNA Automation</a>, <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf" target="_blank">CCNP Automation</a>, and <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf" target="_blank">CCIE Automation</a></li>
                <li><a href="https://www.cisco.com/site/us/en/learn/training-certifications/certifications/devnet/index.html" target="_blank">DevNet</a> (Associate, Specialist, Professional, Expert)</li>
                <li><a href="https://www.cisco.com/site/us/en/learn/training-certifications/exams/enauto.html" target="_blank">Automating Cisco Enterprise Solutions (ENAUTO)</a></li>
                <li><a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf" target="_blank">Automating Cisco Data Center Networking Solutions (DCNAUTO)</a></li>
            </ul>

            <h4>What I Can Help With</h4>
            <ul>
                <li><strong>Certification Guidance</strong>: Get expert advice on exam preparation strategies</li>
                <li><strong>Technical Questions</strong>: Deep dive into YANG, NETCONF, RESTCONF, APIs, and automation frameworks</li>
                <li><strong>Learning Resources</strong>: Discover the best Cisco U. courses, DevNet labs, and practice exams</li>
                <li><strong>Hands-On Practice</strong>: Find sandbox environments and practical exercises</li>
                <li><strong>Career Planning</strong>: Navigate your automation certification journey</li>
            </ul>

            <h4>Key Resources I'll Source From and Recommend</h4>
            <ul>
                <li><strong><a href="https://www.cisco.com/site/us/en/learn/training-certifications/index.html" target="_blank">Learn with Cisco</a></strong> - Explore limitless learning opportunities for skills development, industry-recognized certifications, and product training.</li>
                <li><strong><a href="https://u.cisco.com" target="_blank">Cisco U.</a></strong> - Official, specially-curated learning paths, courses, tutorials, practice exams, and more</li>
                <li><strong><a href="https://learningnetwork.cisco.com" target="_blank">Cisco Learning Network</a></strong> - Helpful community, exam prep, and expert discussions</li>
                <li><strong><a href="https://netacad.com" target="_blank">Cisco Networking Academy</a></strong> - Free online courses, in-person learning, certification-aligned pathways</li>
                <li><strong><a href="https://developer.cisco.com" target="_blank">Cisco DevNet</a></strong> - Developer resources to innovate, code, and build</li>
                <li><strong><a href="https://developer.cisco.com/learning/" target="_blank">DevNet Learning Labs</a></strong> - Hands-on automation practice to improve knowledge and skills</li>
                <li><strong><a href="https://developer.cisco.com/site/sandbox/" target="_blank">DevNet Sandboxes</a></strong> - Free lab environments for learning and testing</li>
                <li><strong><a href="https://developer.cisco.com/docs/" target="_blank">DevNet Docs</a></strong> - Technical documentation for all Cisco-related technologies</li>
            </ul>

            <h4>Ready to Get Started?</h4>
            <p>Ask me anything about Cisco automation certifications! Try questions like:</p>
            <ul>
                <li>"How do I prepare for CCNA Automation?"</li>
                <li>"What's the difference between NETCONF and RESTCONF?"</li>
                <li>"When do DevNet certifications retire?"</li>
                <li>"Show me the best learning path for network automation"</li>
            </ul>
            <p><strong>Let's accelerate your automation certification journey!</strong></p>
        </div>

        <!-- Certification image -->
        {f'<div class="cert-image"><img src="{cert_image_base64}" alt="Automation Certification Badges"></div>' if cert_image_base64 else ''}
        
        {f'<p style="text-align: center; margin: 20px 0;"><strong>Beginning February 3, 2026, Cisco DevNet certifications will evolve to an Automation track. These updated certifications feature major updates to the exams and training materials with an even greater focus on automation and AI-ready networking skills.</strong></p>' if cert_image_base64 else ''}

        <!-- Footer -->
        <div class="footer">
            Built with ❤️ for the <a href="https://learningnetwork.cisco.com/s/communities" target="_blank">Cisco Certification Communities</a> | 
            Open Source | 
            Powered by Google Gemini AI
        </div>
    </div>



    <script>
        const chatForm = document.getElementById('chatForm');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const chatMessages = document.getElementById('chatMessages');

        let conversationHistory = [];

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
                // Send message to API
                const response = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        message: userInput,
                        conversation_history: conversationHistory
                    }})
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    addMessage(data.response, 'bot');
                    
                    // Update conversation history
                    conversationHistory.push(
                        {{ role: 'user', content: userInput }},
                        {{ role: 'assistant', content: data.response }}
                    );
                }} else {{
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }}
            }} catch (error) {{
                addMessage('Sorry, I encountered a network error. Please try again.', 'bot');
            }} finally {{
                // Hide loading and re-enable form
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
            
            chatMessages.prepend(messageDiv); /* newest on top */
            // No auto-scroll needed since messages appear at top
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function formatResponse(text) {{
            // Convert markdown-like formatting to HTML
            let formatted = text
                // Convert markdown links [text](url) to HTML links
                .replace(/\\[(.*?)\\]\\((https?:[^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>')
                // Convert ** to strong
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                // Convert remaining *text* to italics
                .replace(/\\*([^\\*]+)\\*/g, '<em>$1</em>')
                // Convert code blocks
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                // Convert newlines to <br/>
                .replace(/\\n/g, '<br/>')
                // Only convert bullet points in lists
                .replace(/^\\* (.*)$/gm, function(match, content) {
                    // Only add bullet if it's part of a list (multiple lines starting with *)
                    if (text.match(/(^|\n)\\* .*(\n\\* .*)+/)) {
                        return '• ' + content;
                    }
                    return content;
                });
            
            return formatted;
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
    """Chat endpoint that uses the hybrid RAG system"""
    global models_loaded
    
    try:
        data = await request.json()
        user_message = data.get("message", "")
        conversation_history = data.get("conversation_history", [])
        
        if not user_message.strip():
            return JSONResponse(
                content={"error": "Message cannot be empty"},
                status_code=400
            )
        
        if not models_loaded:
            return JSONResponse(
                content={"error": "Models are still loading. Please wait a moment and try again."},
                status_code=503
            )
        
        # Use the same chat function from hybrid_rag_gpt
        response = chat(user_message, conversation_history)
        
        return JSONResponse(content={"response": response})
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return JSONResponse(
            content={"error": "An error occurred while processing your request"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting FastAPI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
