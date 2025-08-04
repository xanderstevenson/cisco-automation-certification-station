#!/usr/bin/env python3
"""
Cisco Automation Certification Station - Streamlit Version
Open-source alternative to Chainlit for commercial deployment
"""

import streamlit as st
import os
from hybrid_rag_gpt import chat
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Cisco Automation Certification Station",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

/* Ensure main container has white background */
.main .block-container {
    background-color: white !important;
}

/* Main app styling */
.main {
    padding: 1rem 2rem !important;
    color: #000000 !important;
    background-color: white !important;
}

/* Reduce top margin */
.main .block-container {
    padding-top: 1rem !important;
    background-color: white !important;
}

/* Header styling */
.cisco-header {
    text-align: center;
    margin-bottom: 1rem;
}

.cisco-logo {
    display: block;
    margin: 0 auto 1rem auto;
    max-width: 400px;
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header with logo
st.markdown('<div class="cisco-header">', unsafe_allow_html=True)

# Display logo if it exists - centered with minimal spacing
logo_path = "public/Cisco-automation-certification-station.png"
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path)
        # Center the image with better column ratio
        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            st.image(logo, use_container_width=False)
    except:
        st.markdown("### 🔧 Cisco Automation Certification Station")
else:
    st.markdown("### 🔧 Cisco Automation Certification Station")

st.markdown('</div>', unsafe_allow_html=True)

# Chat interface right after logo
st.markdown("### 💬 Ask Your Certification Questions")
user_input = st.text_input("Ask about Cisco automation certifications, exam preparation, or technical topics:", key="user_input")

if st.button("Send", key="send_button"):
    if user_input:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show thinking indicator
        with st.spinner("⚡ Searching Cisco documentation and generating comprehensive response..."):
            # Get response from hybrid RAG system
            response = chat(user_input)
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear input (rerun will show empty input)
        st.rerun()

# Display chat messages if any exist
if st.session_state.messages:
    st.markdown("---")
    st.markdown("### 💬 Conversation")
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong>Cisco Expert:</strong><br/><br/>{message["content"]}</div>', unsafe_allow_html=True)

# Welcome content below chat (or initially visible)
st.markdown("---")

# Welcome message with normal paragraph text
st.markdown("""
Welcome to your AI-powered Cisco automation certification advisor. I'm here to help you improve your knowledge in and skills with Cisco network automation technologies and prepare you for certifications including:

- [CCNA Automation](https://learningnetwork.cisco.com/s/ccnaauto-exam-topics)
- [CCNP Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf)
- [CCIE Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf)
- [Automating Cisco Enterprise Solutions (ENAUTO)](https://www.cisco.com/site/us/en/learn/training-certifications/exams/enauto.html)
- [Automating Cisco Data Center Networking Solutions (DCNAUTO)](https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf)

#### What I Can Help With

- **Certification Guidance**: Get expert advice on exam preparation strategies
- **Technical Questions**: Deep dive into YANG, NETCONF, RESTCONF, APIs, and automation frameworks
- **Learning Resources**: Discover the best Cisco U courses, DevNet labs, and practice exams
- **Hands-On Practice**: Find sandbox environments and practical exercises
- **Career Planning**: Navigate your automation certification journey

#### Key Resources I'll Recommend

- **[Cisco U](https://u.cisco.com)** - Official training paths and practice exams
- **[Cisco Networking Academy](https://www.netacad.com)** - Free online courses, in-person learning, certification-aligned pathways
- **[Cisco Learning Network](https://learningnetwork.cisco.com)** - Community, exam prep, and expert discussions
- **[DevNet Learning Labs](https://developer.cisco.com/learning/)** - Hands-on automation practice
- **[DevNet Sandbox](https://developer.cisco.com/site/sandbox/)** - Free lab environments

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
        # Center the certification image
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(cert_image, use_container_width=True)
        
        # Add certification evolution text
        st.markdown("""
        **Beginning February 3, 2026, Cisco DevNet certifications will evolve to an Automation track. These updated certifications feature major updates to the exams and training materials with an even greater focus on automation and AI-ready networking skills.**
        """)
    except:
        pass

# Sidebar with additional information
with st.sidebar:
    st.markdown("## 📚 Resources")
    st.markdown("""
    **Official Cisco Learning:**
    - [Cisco U](https://u.cisco.com)
    - [Cisco Learning Network](https://learningnetwork.cisco.com)
    - [DevNet](https://developer.cisco.com)
    
    **System Features:**
    - 📄 11 Official Cisco PDFs
    - 🌐 Real-time web search
    - 🤖 Google Gemini AI
    - ⚡ Sub-second responses
    """)
    
    st.markdown("## ⚙️ System Status")
    st.success("✅ Hybrid RAG System Online")
    st.info("📊 209 Document Chunks Indexed")
    st.info("🔍 FAISS Vector Search Ready")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    Built with ❤️ for the Cisco certification community | 
    <a href="https://github.com/your-repo" target="_blank">Open Source</a> | 
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
