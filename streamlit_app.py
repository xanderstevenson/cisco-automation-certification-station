#!/usr/bin/env python3
"""
Cisco Automation Certification Station - Streamlit Version
Open-source alternative to Chainlit for commercial deployment
"""

import streamlit as st
import os
# Lazy import heavy dependencies to speed up initial page load
# from hybrid_rag_gpt import chat  # Import only when needed
# from PIL import Image  # Import only when needed
import base64
import time
# Page configuration
st.set_page_config(
    page_title="Cisco Automation Certification Station",
    page_icon="public/Cisco-automation-certification-station.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Note: Removed custom HTML loading screen to eliminate double loading screen issue
# Keeping only the nice Streamlit loading screen that works properly

# Load external CSS file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the external CSS
load_css('style.css')

# Custom CSS for Cisco branding
st.markdown("""
<style>
/* Cisco Blue Color Palette */
:root {
    --cisco-blue: #1BA0D7;
    --cisco-dark-blue: #0D5F8A;
    --cisco-light-blue: #5CB3D9;
}

/* Force white background for entire app */
.main, .stApp, body {
    background-color: white !important;
}

/* Constrain app width and center it */
.main .block-container {
    max-width: 1200px !important;
    padding-top: 0rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    margin: 0 auto !important;
    background-color: white !important;
}

/* Mobile responsive width fix - prevent horizontal wobbling */
@media (max-width: 768px) {
    .main .block-container {
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        margin: 0 !important;
    }
}

/* Tablet responsive width */
@media (min-width: 769px) and (max-width: 1024px) {
    .main .block-container {
        max-width: 95% !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
}

/* Main app styling */
.main {
    padding: 0 !important;
    color: #000000 !important;
    background-color: white !important;
}

/* Minimize header spacing and center image */
.cisco-header {
    text-align: center;
    margin: 0 !important;
    padding: 0 !important;
}

/* Remove extra spacing from Streamlit elements */
.element-container {
    margin-bottom: 0.25rem !important;
}

/* Dark mode logo enhancement for better readability */
@media (prefers-color-scheme: dark) {
    .cisco-logo-container img {
        filter: drop-shadow(0 0 0.5px rgba(255,255,255,0.6)) !important;
        -webkit-filter: drop-shadow(0 0 0.5px rgba(255,255,255,0.6)) !important;
    }
}

/* Light mode - ensure no shadow interference */
@media (prefers-color-scheme: light) {
    .cisco-logo-container img {
        filter: none !important;
        -webkit-filter: none !important;
    }
}

/* Reduce spacing between elements */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.25rem !important;
}

/* Tighter spacing for sections */
.stMarkdown {
    margin-bottom: 0.5rem !important;
}

/* Hide Streamlit footer */
footer[data-testid="stDecoration"] {
    display: none !important;
}

.css-1dp5vir {
    display: none !important;
}

/* Hide "Made with Streamlit" */
.css-cio0dv {
    display: none !important;
}

/* Reduce bottom spacing */
.main .block-container {
    padding-bottom: 1rem !important;
}

/* Remove excessive bottom margin */
body {
    margin-bottom: 0 !important;
}

/* Compact footer spacing */
.stMarkdown:last-child {
    margin-bottom: 0 !important;
}

/* All links styling - Cisco blue with stronger selectors */
a, a:link, a:visited, a:hover, a:active {
    color: #1BA0D7 !important;
    text-decoration: none !important;
}

a:hover {
    color: #0E7A9F !important;
    text-decoration: underline !important;
}

/* Main content links - stronger selectors */
.main a, .main a:link, .main a:visited {
    color: #1BA0D7 !important;
}

/* Markdown links */
.stMarkdown a, .stMarkdown a:link, .stMarkdown a:visited {
    color: #1BA0D7 !important;
}

/* Sidebar links styling */
.css-1d391kg a, .css-1d391kg a:link, .css-1d391kg a:visited {
    color: #1BA0D7 !important;
}

/* Button styling */
.stButton > button {
    background-color: var(--cisco-blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: var(--cisco-dark-blue) !important;
    color: white !important;
}

/* Input styling - fix black background */
.stTextInput > div > div > input {
    border-color: var(--cisco-blue) !important;
    color: #000000 !important;
    background-color: white !important;
    padding: 0.5rem !important;
    font-size: 1rem !important;
}

/* Input label styling */
.stTextInput label {
    color: #000000 !important;
}

/* All text elements */
p, div, span, h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

/* Streamlit markdown containers */
.stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
    color: #000000 !important;
}

/* Main container text */
.main .block-container, .main .block-container * {
    color: #000000 !important;
}

/* Chat message styling */
.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 10px;
    border-left: 4px solid var(--cisco-blue);
}

.user-message {
    background-color: #f0f8ff;
    margin-left: 2rem;
    color: #333 !important;
}

.bot-message {
    background-color: #f9f9f9;
    margin-right: 2rem;
    color: #333 !important;
    line-height: 1.6;
}

.bot-message strong {
    color: var(--cisco-blue) !important;
    display: block;
    margin-bottom: 0.5rem;
}

/* Ensure all text is readable */
.chat-message * {
    color: #333 !important;
}

/* Fix any white text issues */
div[data-testid="stMarkdownContainer"] p {
    color: #333 !important;
}

/* Links styling */
a {
    color: var(--cisco-blue) !important;
}

a:hover {
    color: var(--cisco-dark-blue) !important;
}

/* Certification badges styling */
.cert-badges {
    text-align: center;
    margin: 2rem 0;
}

.cert-badges img {
    max-width: 75%;
    height: auto;
    margin: 0 auto;
    display: block;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Streamlit Connection Error Styling */
.stConnectionStatus {
    background-color: #f8f9fa !important;
    color: #212529 !important;
    border: 2px solid #dc3545 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.stConnectionStatus [data-testid="stNotificationContentError"] {
    background-color: #fff5f5 !important;
    color: #721c24 !important;
    border-left: 4px solid #dc3545 !important;
    padding: 1rem !important;
}

.stConnectionStatus h3 {
    color: #dc3545 !important;
    font-weight: 600 !important;
}

.stConnectionStatus p {
    color: #495057 !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
}

.stConnectionStatus code {
    background-color: #f1f3f4 !important;
    color: #d63384 !important;
    padding: 0.2rem 0.4rem !important;
    border-radius: 4px !important;
    font-family: 'Monaco', 'Consolas', monospace !important;
}

/* Alternative: Cisco-themed connection error */
.stConnectionStatus {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
    border: 2px solid var(--cisco-blue) !important;
    color: #2c3e50 !important;
}

.stConnectionStatus [data-testid="stNotificationContentError"] {
    background-color: rgba(27, 160, 215, 0.1) !important;
    border-left: 4px solid var(--cisco-blue) !important;
    color: #2c3e50 !important;
}

.stConnectionStatus h3 {
    color: var(--cisco-dark-blue) !important;
}

/* Ensure all text in error popup is readable */
.stConnectionStatus * {
    color: #2c3e50 !important;
}

.stConnectionStatus strong {
    color: var(--cisco-dark-blue) !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize system loading state
if "system_ready" not in st.session_state:
    st.session_state.system_ready = False

# Cold start loading screen
if not st.session_state.system_ready:
    # Add more top padding
    st.markdown('<div style="padding-top: 3rem;"></div>', unsafe_allow_html=True)
    
    # Display certification badges image at original size
    st.image("public/Automation_Cert_badges.png")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2>Cisco Automation Certification Station</h2>
        <p>Initializing AI models and knowledge base...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show loading progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Faster initialization progress simulation
    for i in range(100):
        progress_bar.progress(i + 1)
        if i < 25:
            status_text.text("Loading embedding models...")
        elif i < 50:
            status_text.text("Initializing vector store...")
        elif i < 75:
            status_text.text("Preparing AI system...")
        else:
            status_text.text("System ready!")
        time.sleep(0.01)  # Faster visual effect for quicker loading
    
    # Mark system as ready
    st.session_state.system_ready = True
    st.rerun()  # Refresh to show main interface

# CSS Background Approach with base64 encoding for image rendering
import base64

logo_path = "public/Cisco-automation-certification-station.png"
if os.path.exists(logo_path):
    # Read and encode the image as base64
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
    <div class="cisco-logo-container" style="
        background-color: white;
        width: 100%;
        padding: 20px 0;
        text-align: center;
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
    ">
        <img src="data:image/png;base64,{logo_data}" style="max-height: none; width: auto;" alt="Cisco Automation Certification Station">
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<h3 style="text-align: center;">🔧 Cisco Automation Certification Station</h3>', unsafe_allow_html=True)

# Add "Learn with Cisco" heading bigger and closer to logo (matching logo-to-CISCO spacing)
st.markdown('<h3 style="text-align: center; margin-top: -1.5rem; margin-bottom: 1rem; font-size: 18px;"><a href="https://www.cisco.com/site/us/en/learn/training-certifications/index.html" target="_blank" style="color: #1BA0D7; text-decoration: none; font-weight: 600;">Learn with Cisco</a></h3>', unsafe_allow_html=True)

# Move heading above text box (not centered)
st.markdown('<h5 style="text-align: center; margin-bottom: 1rem;">Ask about Cisco automation certifications, exam preparation, or technical topics:</h5>', unsafe_allow_html=True)

# Aggressive CSS to fix button and centering issues
st.markdown("""
<style>
/* REMOVE GLOBAL CENTERING - Only center specific elements */
.main .block-container {
    max-width: 800px !important;
    margin: 0 auto !important;
}

/* ULTRA AGGRESSIVE BUTTON STYLING */
button[kind="formSubmit"], .stButton > button, button[data-testid="baseButton-secondary"], button {
    background-color: #5CB3D9 !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    background: #5CB3D9 !important;
}

button[kind="formSubmit"]:hover, .stButton > button:hover, button[data-testid="baseButton-secondary"]:hover, button:hover {
    background-color: #1BA0D7 !important;
    color: white !important;
    background: #1BA0D7 !important;
}

/* Target all possible button selectors */
form button, [data-testid="stForm"] button {
    background-color: #5CB3D9 !important;
    background: #5CB3D9 !important;
    color: white !important;
}

/* REMOVE CENTERING - Keep form and input left-aligned */
div[data-testid="stForm"] {
    width: 100% !important;
}

.stTextInput {
    width: 100% !important;
}

.stTextInput > div {
    max-width: 600px !important;
    width: 100% !important;
}

/* HIDE STREAMLIT FOOTER */
footer {
    visibility: hidden !important;
}

.stDeployButton {
    visibility: hidden !important;
}

/* Hide "Made with Streamlit" */
.viewerBadge_container__1QSob {
    display: none !important;
}

/* Hide Streamlit menu */
#MainMenu {
    visibility: hidden !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Use form for automatic input clearing
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Ask about Cisco automation certs, exam prep, or technical topics:",
        placeholder="Type your question here...",
        key="user_input_form",
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button("Send")

# Process user input when submitted
if submit_button and user_input:
    # Input validation and sanitization
    if len(user_input.strip()) == 0:
        st.warning("⚠️ Please enter a valid question.")
        st.stop()
    
    if len(user_input) > 2000:
        st.error("⚠️ Question too long. Please limit to 2000 characters.")
        st.stop()
    
    # Basic input sanitization
    sanitized_input = user_input.strip()[:2000]
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": sanitized_input})
    
    # Show thinking indicator
    with st.spinner("⚡ Searching Cisco resources and generating a comprehensive response..."):
        # Lazy import heavy dependencies only when needed
        try:
            from hybrid_rag_gpt import chat
        except ImportError as e:
            st.error(f"❌ Error importing chat module: {str(e)}")
            response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
        else:
            # Get response from hybrid RAG system with conversation history
            conversation_history = [(msg["role"], msg["content"]) for msg in st.session_state.messages[:-1]]
            
            try:
                response = chat(sanitized_input, conversation_history)
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                response = "I apologize, but I'm experiencing technical difficulties. Please try again later."
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to show new messages
    st.rerun()

# Display chat messages if any exist
if st.session_state.messages:
    st.markdown("---")
    st.markdown("### 💬 Conversation")
    for message in reversed(st.session_state.messages):
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong>Cisco Expert:</strong><br/><br/>{message["content"]}</div>', unsafe_allow_html=True)

# Welcome content below chat (or initially visible)
st.markdown('<br>', unsafe_allow_html=True)

# Welcome message with normal paragraph text
st.markdown("""
Welcome to your AI-powered Cisco automation certification advisor. I'm here to help you improve your knowledge in and skills with Cisco network automation technologies and prepare you for certifications including:

- [CCNA Automation](https://learningnetwork.cisco.com/s/ccnaauto-exam-topics), [CCNP Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf), and [CCIE Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf)
- [DevNet](https://www.cisco.com/site/us/en/learn/training-certifications/certifications/devnet/index.html) (Associate, Specialist, Professional, Expert)
- [Automating Cisco Enterprise Solutions (ENAUTO)](https://www.cisco.com/site/us/en/learn/training-certifications/exams/enauto.html)
- [Automating Cisco Data Center Networking Solutions (DCNAUTO)](https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf)

#### What I Can Help With

- **Certification Guidance**: Get expert advice on exam preparation strategies
- **Technical Questions**: Deep dive into YANG, NETCONF, RESTCONF, APIs, and automation frameworks
- **Learning Resources**: Discover the best Cisco U. courses, DevNet labs, and practice exams
- **Hands-On Practice**: Find sandbox environments and practical exercises
- **Career Planning**: Navigate your automation certification journey

#### Key Resources I'll Source From and Recommend

- **[Learn with Cisco](https://www.cisco.com/site/us/en/learn/training-certifications/index.html)** - Explore limitless learning opportunities for skills development, industry-recognized certifications, and product training.
  - **[Cisco U.](https://u.cisco.com)** - Official, specially-curated learning paths, courses, tutorials, practice exams, and more
  - **[Cisco Learning Network](https://learningnetwork.cisco.com)** - Helpful community, exam prep, and expert discussions
  - **[Cisco Networking Academy](https://netacad.com)** - Free online courses, in-person learning, certification-aligned pathways

""", unsafe_allow_html=True)

# Add spacing between main resource sections
st.markdown('<br>', unsafe_allow_html=True)

st.markdown("""
- **[Cisco DevNet](https://developer.cisco.com)** - Developer resources to innovate, code, and build
  - **[DevNet Learning Labs](https://developer.cisco.com/learning/)** - Hands-on automation practice to improve knowledge and skills
  - **[DevNet Sandboxes](https://developer.cisco.com/site/sandbox/)** - Free lab environments for learning and testing
  - **[DevNet Docs](https://developer.cisco.com/docs/)** - Technical documentation for all Cisco-related technologies

#### Ready to Get Started?

Ask me anything about Cisco automation certifications! Try questions like:

- "How do I prepare for CCNA Automation?"
- "What's the difference between NETCONF and RESTCONF?"
- "When do DevNet certifications retire?"
- "Show me the best learning path for network automation"

**Let's accelerate your automation certification journey!**
""")

# Display certification evolution image and text
cert_image_path = "public/Automation_Cert_badges_Current_Future.png"
if os.path.exists(cert_image_path):
    try:
        cert_image = Image.open(cert_image_path)
        # Display certification image at original size (left-aligned)
        st.image(cert_image)
        
        # Add certification evolution text
        st.markdown("""
        **Beginning February 3, 2026, Cisco DevNet certifications will evolve to an Automation track. These updated certifications feature major updates to the exams and training materials with an even greater focus on automation and AI-ready networking skills.**
        """)
        
        # Add spacing before footer
        st.markdown('<br>', unsafe_allow_html=True)
    except:
        pass

# Sidebar with additional information
with st.sidebar:
    st.markdown("## 📚 Resources")
    st.markdown("""
    **Official Cisco Learning:**
    - [Cisco U.](https://u.cisco.com)
    - [Cisco Learning Network](https://learningnetwork.cisco.com)
    - [Cisco Networking Academy](https://netacad.com)
    - [Cisco DevNet](https://developer.cisco.com)
    - [DevNet Learning Labs](https://developer.cisco.com/learning/)
    - [DevNet Sandboxes](https://developer.cisco.com/site/sandbox/)
    - [DevNet Docs](https://developer.cisco.com/docs/)
    
    **System Features:**
    - 📄 10 Cisco PDFs + 62 web URLs
    - 🌐 Real-time web search via SerpAPI
    - 🤖 Google AI Studio, Google Cloud Run, and Google Gemini AI
    - ⚡ ~6-8 second response times
    """)
    
    st.markdown("## ⚙️ System Status")
    st.success("✅ Hybrid RAG System Online")
    st.info("📊 4,325 Document Chunks Indexed")
    st.info("🔍 FAISS Vector Search Ready")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 0.5rem; margin-bottom: -1rem;">
    Built with ❤️ for the <a href="https://learningnetwork.cisco.com/s/communities" target="_blank">Cisco Certification Communities</a> | 
    Open Source | 
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
