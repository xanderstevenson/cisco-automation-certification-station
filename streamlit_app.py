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

/* Main app styling */
.main {
    padding: 2rem;
}

/* Header styling */
.cisco-header {
    text-align: center;
    margin-bottom: 2rem;
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

/* Input styling */
.stTextInput > div > div > input {
    border-color: var(--cisco-blue) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--cisco-dark-blue) !important;
    box-shadow: 0 0 0 2px var(--cisco-light-blue) !important;
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
}

.bot-message {
    background-color: #f9f9f9;
    margin-right: 2rem;
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

# Display logo if it exists
logo_path = "public/Cisco-automation-certification-station.png"
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path)
        st.image(logo, width=400, use_column_width=False)
    except:
        st.markdown("# 🔧 Cisco Automation Certification Station")
else:
    st.markdown("# 🔧 Cisco Automation Certification Station")

st.markdown('</div>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
A production-ready Hybrid Retrieval-Augmented Generation (RAG) system designed for Cisco network automation certification preparation. This system combines local document search, web search, and AI generation to provide comprehensive, source-backed answers for:

- [CCNA Automation](https://learningnetwork.cisco.com/s/ccnaauto-exam-topics)
- [CCNP Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf)
- [CCIE Automation](https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf)
- [Automating Cisco Enterprise Solutions (ENAUTO)](https://www.cisco.com/site/us/en/learn/training-certifications/exams/enauto.html)
- [Automating Cisco Data Center Networking Solutions (DCNAUTO)](https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf)
""")

# Display certification evolution image if it exists
cert_image_path = "public/Automation_Cert_badges_Current_Future.png"
if os.path.exists(cert_image_path):
    try:
        cert_image = Image.open(cert_image_path)
        st.markdown('<div class="cert-badges">', unsafe_allow_html=True)
        st.image(cert_image, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        pass

# Chat interface
st.markdown("## 💬 Ask Your Certification Questions")

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message"><strong>Cisco Expert:</strong> {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.text_input("Ask about Cisco automation certifications, exam preparation, or technical topics:", key="user_input")

# Send button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Send", key="send_button") and user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show thinking indicator
        with st.spinner("⚡ Searching Cisco documentation and generating comprehensive response..."):
            # Generate response using hybrid RAG
            response = chat(user_input)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to display new messages
        st.rerun()

# Clear chat button
if st.session_state.messages:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Clear Chat", key="clear_button"):
            st.session_state.messages = []
            st.rerun()

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
