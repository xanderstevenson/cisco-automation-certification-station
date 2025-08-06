#!/usr/bin/env python3
"""
Cisco Automation Certification Station - Streamlit Version
Open-source alternative to Chainlit for commercial deployment
"""

import streamlit as st
import os
from hybrid_rag_gpt import chat
from PIL import Image
import base64
import requests
import json
import time
from datetime import datetime
# Page configuration
st.set_page_config(
    page_title="Cisco Automation Certification Station",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

/* API Testing Tool Styles */
.api-tool-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    font-family: 'Source Sans Pro', sans-serif;
}

.api-tool-trigger {
    background: linear-gradient(135deg, #1BA0D7, #0D5F8A);
    color: white;
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(27, 160, 215, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: all 0.3s ease;
}

.api-tool-trigger:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(27, 160, 215, 0.4);
}

.api-tool-panel {
    position: absolute;
    top: 70px;
    right: 0;
    width: 400px;
    max-height: 600px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    border: 1px solid #e0e0e0;
    overflow-y: auto;
    display: none;
}

.api-tool-panel.active {
    display: block;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.api-tool-header {
    background: linear-gradient(135deg, #1BA0D7, #0D5F8A);
    color: white;
    padding: 15px 20px;
    border-radius: 12px 12px 0 0;
    font-weight: 600;
    font-size: 16px;
}

.api-tool-content {
    padding: 20px;
}

.api-form-group {
    margin-bottom: 15px;
}

.api-form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #333;
    font-size: 14px;
}

.api-form-group input, .api-form-group select, .api-form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: border-color 0.3s ease;
}

.api-form-group input:focus, .api-form-group select:focus, .api-form-group textarea:focus {
    outline: none;
    border-color: #1BA0D7;
}

.api-preset-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
}

.api-preset-btn {
    background: #f0f8ff;
    color: #1BA0D7;
    border: 1px solid #1BA0D7;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.api-preset-btn:hover {
    background: #1BA0D7;
    color: white;
}

.api-send-btn {
    background: linear-gradient(135deg, #1BA0D7, #0D5F8A);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    transition: all 0.3s ease;
}

.api-send-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(27, 160, 215, 0.3);
}

.api-send-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
}

.api-response-container {
    margin-top: 20px;
    border-top: 1px solid #e0e0e0;
    padding-top: 20px;
}

.api-response-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.api-status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.api-status-success {
    background: #d4edda;
    color: #155724;
}

.api-status-error {
    background: #f8d7da;
    color: #721c24;
}

.api-response-body {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.api-code-section {
    margin-top: 15px;
    border-top: 1px solid #e0e0e0;
    padding-top: 15px;
}

.api-code-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.api-code-tab {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.api-code-tab.active {
    background: #1BA0D7;
    color: white;
    border-color: #1BA0D7;
}

.api-code-block {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    max-height: 150px;
    overflow-y: auto;
}

@media (max-width: 768px) {
    .api-tool-panel {
        width: 350px;
        right: -10px;
    }
    
    .api-tool-trigger {
        width: 50px;
        height: 50px;
        font-size: 20px;
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

# Cisco API Testing Tool Functions
def get_cisco_api_presets():
    """Return predefined Cisco API endpoints for educational purposes"""
    return {
        "DNA Center - Network Devices": {
            "url": "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer <your_token_here>"
            },
            "description": "Get all network devices from DNA Center"
        },
        "Meraki Dashboard - Organizations": {
            "url": "https://api.meraki.com/api/v1/organizations",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json",
                "X-Cisco-Meraki-API-Key": "<your_api_key_here>"
            },
            "description": "List all organizations in Meraki Dashboard"
        },
        "Webex Teams - List Rooms": {
            "url": "https://webexapis.com/v1/rooms",
            "method": "GET",
            "headers": {
                "Authorization": "Bearer <your_access_token>",
                "Content-Type": "application/json"
            },
            "description": "List Webex Teams rooms"
        },
        "APIC-EM - Get Ticket": {
            "url": "https://sandboxapic.cisco.com/api/v1/ticket",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": '{"username": "devnetuser", "password": "Cisco123!"}',
            "description": "Get authentication ticket from APIC-EM"
        },
        "NSO - Get Device List": {
            "url": "http://localhost:8080/restconf/data/tailf-ncs:devices/device",
            "method": "GET",
            "headers": {
                "Accept": "application/yang-data+json",
                "Authorization": "Basic YWRtaW46YWRtaW4="
            },
            "description": "Get device list from Cisco NSO"
        }
    }

def generate_code_examples(method, url, headers, body=None):
    """Generate Python and JavaScript code examples for the API call"""
    python_code = f"""# Python example using requests
import requests
import json

url = "{url}"
headers = {json.dumps(headers, indent=4)}
"""
    
    if body and method in ['POST', 'PUT', 'PATCH']:
        python_code += f"\ndata = {body}\n"
        python_code += f"\nresponse = requests.{method.lower()}(url, headers=headers, data=data)"
    else:
        python_code += f"\nresponse = requests.{method.lower()}(url, headers=headers)"
    
    python_code += "\nprint(f'Status: {response.status_code}')\nprint(f'Response: {response.json()}')"
    
    js_code = f"""// JavaScript example using fetch
const url = "{url}";
const headers = {json.dumps(headers, indent=4)};

const options = {{
    method: "{method}",
    headers: headers"""
    
    if body and method in ['POST', 'PUT', 'PATCH']:
        js_code += f",\n    body: {body}"
    
    js_code += "\n};\n\nfetch(url, options)\n    .then(response => response.json())\n    .then(data => console.log(data))\n    .catch(error => console.error('Error:', error));"
    
    return python_code, js_code

def make_api_request(method, url, headers, body=None):
    """Make API request with error handling and educational feedback"""
    try:
        # Parse headers if string
        if isinstance(headers, str):
            headers = json.loads(headers) if headers.strip() else {}
        
        # Parse body if string
        if body and isinstance(body, str):
            try:
                body = json.loads(body)
            except:
                pass  # Keep as string if not valid JSON
        
        start_time = time.time()
        
        # Make the request
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=body if isinstance(body, dict) else None, 
                                   data=body if isinstance(body, str) else None, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=body if isinstance(body, dict) else None,
                                  data=body if isinstance(body, str) else None, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=body if isinstance(body, dict) else None,
                                    data=body if isinstance(body, str) else None, timeout=10)
        else:
            return None, f"Unsupported HTTP method: {method}"
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        # Format response
        try:
            response_json = response.json()
            formatted_response = json.dumps(response_json, indent=2)
        except:
            formatted_response = response.text
        
        result = {
            'status_code': response.status_code,
            'response_time': response_time,
            'headers': dict(response.headers),
            'body': formatted_response,
            'success': 200 <= response.status_code < 300
        }
        
        return result, None
        
    except requests.exceptions.Timeout:
        return None, "Request timed out (10s). Check if the API endpoint is accessible."
    except requests.exceptions.ConnectionError:
        return None, "Connection error. Check if the URL is correct and accessible."
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def explain_api_response(status_code, response_body):
    """Provide educational explanation of API response"""
    explanations = {
        200: "✅ Success! The request was processed successfully.",
        201: "✅ Created! A new resource was successfully created.",
        204: "✅ No Content! The request was successful but there's no content to return.",
        400: "❌ Bad Request! Check your request format, parameters, or body.",
        401: "🔐 Unauthorized! Check your authentication credentials (API key, token, etc.).",
        403: "🚫 Forbidden! You don't have permission to access this resource.",
        404: "🔍 Not Found! The requested resource doesn't exist. Check the URL.",
        405: "⚠️ Method Not Allowed! This HTTP method is not supported for this endpoint.",
        429: "⏱️ Rate Limited! You're making too many requests. Wait before trying again.",
        500: "🔥 Server Error! There's an issue on the server side.",
        502: "🌐 Bad Gateway! The server received an invalid response from upstream.",
        503: "🚧 Service Unavailable! The service is temporarily down for maintenance."
    }
    
    base_explanation = explanations.get(status_code, f"Status Code {status_code}: Check API documentation for details.")
    
    # Add specific tips based on status code
    tips = []
    if status_code == 401:
        tips.append("💡 Tip: For Cisco APIs, check if you need to authenticate first (like getting a token from APIC-EM).")
    elif status_code == 404:
        tips.append("💡 Tip: Verify the API endpoint URL and any required path parameters.")
    elif status_code == 400:
        tips.append("💡 Tip: Check your JSON syntax and required fields in the request body.")
    
    return base_explanation, tips

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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

# API Testing Tool - Upper Right Floating Icon
st.markdown("""
<!-- API Testing Tool Floating Icon -->
<div class="api-tool-floating-icon" id="apiToolIcon" title="API Testing Tool">
    <span class="api-text-line1">API</span>
    <span class="api-text-line2">Tester</span>
</div>

<!-- API Testing Tool Sidebar Overlay -->
<div class="api-sidebar-overlay" id="apiSidebarOverlay" style="display: none;">
    <div class="api-sidebar">
        <div class="api-header">
            <h3>🔌 Cisco API Tester</h3>
            <button class="api-close-btn" onclick="closeSidebar()">×</button>
        </div>
        <div class="api-sidebar-content">
            <div class="api-section">
                <h3>Quick Start - Cisco API Presets</h3>
                <div class="api-preset-grid" id="apiPresetGrid"></div>
            </div>
            <div class="api-section">
                <h3>API Configuration</h3>
                <div class="api-form-row">
                    <label>Method:</label>
                    <select id="sidebarApiMethod" onchange="updateSidebarMethodFields()">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                    </select>
                </div>
                <div class="api-form-row">
                    <label>URL:</label>
                    <input type="text" id="sidebarApiUrl" placeholder="https://api.example.com/endpoint" />
                </div>
                <div class="api-form-row">
                    <label>Headers:</label>
                    <textarea id="sidebarApiHeaders" rows="3" placeholder='{"Authorization": "Bearer token"}'></textarea>
                </div>
                <div class="api-form-row" id="sidebarApiBodyRow" style="display: none;">
                    <label>Body:</label>
                    <textarea id="sidebarApiBody" rows="3" placeholder='{"key": "value"}'></textarea>
                </div>
                <button class="api-send-button" onclick="sendSidebarApiRequest()" id="sidebarSendBtn">
                    Send Request
                </button>
            </div>
            <div class="api-section" id="sidebarResponseSection" style="display: none;">
                <h3>Response</h3>
                <div id="sidebarResponseStatus"></div>
                <pre id="sidebarResponseBody"></pre>
            </div>
        </div>
    </div>
</div>

<script>
// Enhanced Cisco API Presets with more comprehensive data
const sidebarCiscoApiPresets = {
    "DNA Center - Devices": {
        url: "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device",
        method: "GET",
        headers: '{\n  "Content-Type": "application/json",\n  "Accept": "application/json",\n  "Authorization": "Bearer <your_token>"\n}',
        description: "Get all network devices from DNA Center"
    },
    "Meraki - Organizations": {
        url: "https://api.meraki.com/api/v1/organizations",
        method: "GET",
        headers: '{\n  "Content-Type": "application/json",\n  "X-Cisco-Meraki-API-Key": "<your_api_key>"\n}',
        description: "List all organizations in Meraki Dashboard"
    },
    "Webex - Rooms": {
        url: "https://webexapis.com/v1/rooms",
        method: "GET",
        headers: '{\n  "Authorization": "Bearer <your_token>",\n  "Content-Type": "application/json"\n}',
        description: "List Webex Teams rooms"
    },
    "APIC-EM - Auth": {
        url: "https://sandboxapic.cisco.com/api/v1/ticket",
        method: "POST",
        headers: '{\n  "Content-Type": "application/json"\n}',
        body: '{\n  "username": "devnetuser",\n  "password": "Cisco123!"\n}',
        description: "Get authentication ticket from APIC-EM"
    }
};

// Debug function to check if elements exist
function debugApiTool() {
    console.log('API Tool Debug:');
    console.log('Overlay element:', document.getElementById('apiSidebarOverlay'));
    console.log('Grid element:', document.getElementById('apiPresetGrid'));
    console.log('Method element:', document.getElementById('sidebarApiMethod'));
}

// Main toggle function with error handling
// Simple toggle function
function toggleApiSidebar() {
    console.log('toggleApiSidebar called');
    const overlay = document.getElementById('apiSidebarOverlay');
    if (overlay) {
        const isVisible = overlay.style.display === 'block';
        overlay.style.display = isVisible ? 'none' : 'block';
        console.log('Sidebar toggled:', isVisible ? 'hidden' : 'visible');
        
        if (!isVisible) {
            initSidebarApiTool();
        }
    } else {
        console.error('API sidebar not found');
    }
}

// Close function for the X button
function closeSidebar() {
    const overlay = document.getElementById('apiSidebarOverlay');
    if (overlay) {
        overlay.style.display = 'none';
        console.log('Sidebar closed');
    }
}

// Initialize API Tool with error handling
function initSidebarApiTool() {
    console.log('initSidebarApiTool called');
    try {
        const grid = document.getElementById('apiPresetGrid');
        if (!grid) {
            console.error('API Preset grid not found!');
            return;
        }
        
        // Clear existing buttons
        grid.innerHTML = '';
        
        // Add preset buttons
        Object.keys(sidebarCiscoApiPresets).forEach(name => {
            const preset = sidebarCiscoApiPresets[name];
            const btn = document.createElement('button');
            btn.className = 'api-preset-button';
            btn.innerHTML = `<strong>${name}</strong><br><small>${preset.description}</small>`;
            btn.onclick = () => loadSidebarPreset(name);
            grid.appendChild(btn);
        });
        
        console.log('Added', Object.keys(sidebarCiscoApiPresets).length, 'preset buttons');
    } catch (error) {
        console.error('Error in initSidebarApiTool:', error);
    }
}

// Load preset with feedback
function loadSidebarPreset(name) {
    console.log('Loading preset:', name);
    try {
        const preset = sidebarCiscoApiPresets[name];
        if (!preset) {
            console.error('Preset not found:', name);
            return;
        }
        
        // Set form values
        const methodEl = document.getElementById('sidebarApiMethod');
        const urlEl = document.getElementById('sidebarApiUrl');
        const headersEl = document.getElementById('sidebarApiHeaders');
        const bodyEl = document.getElementById('sidebarApiBody');
        
        if (methodEl) methodEl.value = preset.method;
        if (urlEl) urlEl.value = preset.url;
        if (headersEl) headersEl.value = preset.headers;
        if (bodyEl && preset.body) bodyEl.value = preset.body;
        
        updateSidebarMethodFields();
        
        // Visual feedback
        const btn = event.target.closest('button');
        if (btn) {
            const originalBg = btn.style.backgroundColor;
            btn.style.backgroundColor = '#28a745';
            btn.style.color = 'white';
            setTimeout(() => {
                btn.style.backgroundColor = originalBg;
                btn.style.color = '';
            }, 1000);
        }
        
        console.log('Preset loaded successfully');
    } catch (error) {
        console.error('Error loading preset:', error);
    }
}

// Update method fields
function updateSidebarMethodFields() {
    try {
        const method = document.getElementById('sidebarApiMethod')?.value;
        const bodyRow = document.getElementById('sidebarApiBodyRow');
        
        if (bodyRow) {
            bodyRow.style.display = ['POST', 'PUT', 'PATCH'].includes(method) ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error updating method fields:', error);
    }
}

// Send API request with enhanced feedback
function sendSidebarApiRequest() {
    console.log('sendSidebarApiRequest called');
    try {
        const btn = document.getElementById('sidebarSendBtn');
        const method = document.getElementById('sidebarApiMethod')?.value;
        const url = document.getElementById('sidebarApiUrl')?.value;
        
        if (!url) {
            alert('Please enter an API URL');
            return;
        }
        
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Sending...';
        }
        
        // Simulate API call
        setTimeout(() => {
            const responseSection = document.getElementById('sidebarResponseSection');
            const statusElement = document.getElementById('sidebarResponseStatus');
            const bodyElement = document.getElementById('sidebarResponseBody');
            
            if (statusElement) {
                statusElement.innerHTML = '<span style="color: #28a745; font-weight: bold;">✅ 200 OK</span> <small>(Demo Response)</small>';
            }
            
            if (bodyElement) {
                const mockResponse = {
                    message: "This is a demo response for educational purposes",
                    method: method,
                    endpoint: url,
                    timestamp: new Date().toISOString(),
                    data: {
                        note: "In production, this would show the actual API response",
                        tip: "Use Cisco DevNet Sandbox for real API testing"
                    }
                };
                bodyElement.textContent = JSON.stringify(mockResponse, null, 2);
            }
            
            if (responseSection) {
                responseSection.style.display = 'block';
            }
            
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🚀 Send Request';
            }
            
            console.log('Mock response displayed');
        }, 1500);
    } catch (error) {
        console.error('Error in sendSidebarApiRequest:', error);
    }
}

// Simple direct approach - set up click handler immediately
(function() {
    function setupClickHandler() {
        const icon = document.getElementById('apiToolIcon');
        if (icon) {
            console.log('Setting up API button click handler');
            icon.style.cursor = 'pointer';
            icon.style.pointerEvents = 'auto';
            
            icon.onclick = function(e) {
                console.log('API button clicked!');
                e.preventDefault();
                e.stopPropagation();
                
                const overlay = document.getElementById('apiSidebarOverlay');
                if (overlay) {
                    const isVisible = overlay.style.display === 'block';
                    overlay.style.display = isVisible ? 'none' : 'block';
                    console.log('Sidebar toggled:', isVisible ? 'hidden' : 'visible');
                } else {
                    console.error('Sidebar overlay not found');
                }
                return false;
            };
            
            console.log('API button click handler attached successfully');
        } else {
            console.log('API button not found, retrying in 100ms');
            setTimeout(setupClickHandler, 100);
        }
    }
    
    // Try multiple times to ensure it works
    setupClickHandler();
    setTimeout(setupClickHandler, 500);
    setTimeout(setupClickHandler, 1000);
    setTimeout(setupClickHandler, 2000);
})();

// Simplified setup function
function setupApiToolIcon() {
    const icon = document.getElementById('apiToolIcon');
    if (icon && !icon.hasClickHandler) {
        icon.style.cursor = 'pointer';
        icon.style.pointerEvents = 'auto';
        
        icon.onclick = function(e) {
            console.log('API button clicked via onclick!');
            e.preventDefault();
            e.stopPropagation();
            
            const overlay = document.getElementById('apiSidebarOverlay');
            if (overlay) {
                const isVisible = overlay.style.display === 'block';
                overlay.style.display = isVisible ? 'none' : 'block';
                console.log('Sidebar toggled:', isVisible ? 'hidden' : 'visible');
            }
            return false;
        };
        
        icon.hasClickHandler = true;
        console.log('API tool icon click handler attached');
    }
}

// Dedicated click handler function
function handleApiIconClick(e) {
    console.log('API icon clicked!', e.type);
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    
    // Force toggle the sidebar
    toggleApiSidebar();
    
    return false;
}

// Also try to initialize after a short delay for Streamlit
setTimeout(() => {
    console.log('Delayed initialization check');
    setupApiToolIcon();
    debugApiTool();
}, 1000);

// Additional fallback initialization
setTimeout(() => {
    console.log('Final fallback initialization');
    setupApiToolIcon();
}, 2000);
</script>

<!-- CSS Styling for API Testing Tool -->
<style>
/* API Testing Tool Floating Icon */
.api-tool-floating-icon {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 65px;
    height: 42px;
    background: #1BA0D7;
    border: none;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    z-index: 1000;
    color: white !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.api-text-line1 {
    font-size: 13px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: 0.3px;
    color: white !important;
    margin-bottom: 2px;
}

.api-text-line2 {
    font-size: 11px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: 0.2px;
    color: white !important;
}

.api-tool-floating-icon:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    background: #0D7AA7;
}

/* API Sidebar Overlay */
.api-sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 2000;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.api-sidebar-overlay.active {
    opacity: 1;
    visibility: visible;
}

/* API Sidebar */
.api-sidebar {
    position: absolute;
    top: 0;
    right: 0;
    width: 500px;
    height: 100%;
    background: white;
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    overflow-y: auto;
}

.api-sidebar-overlay.active .api-sidebar {
    transform: translateX(0);
}

/* Sidebar Header */
.api-sidebar-header {
    background: linear-gradient(135deg, #1BA0D7, #0D7AA7);
    color: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.api-sidebar-header h2 {
    margin: 0;
    font-size: 20px;
}

.api-close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s ease;
}

.api-close-btn:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* Sidebar Content */
.api-sidebar-content {
    padding: 20px;
}

.api-section {
    margin-bottom: 30px;
}

.api-section h3 {
    color: #1BA0D7;
    margin-bottom: 15px;
    font-size: 16px;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 5px;
}

/* Preset Grid */
.api-preset-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.api-preset-button {
    background: #f8f9fa;
    border: 2px solid #e0e0e0;
    padding: 12px 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 11px;
    text-align: center;
    line-height: 1.3;
}

.api-preset-button:hover {
    border-color: #1BA0D7;
    background: #f0f8ff;
    transform: translateY(-1px);
}

.api-preset-button strong {
    color: #1BA0D7;
    display: block;
    margin-bottom: 4px;
}

.api-preset-button small {
    color: #666;
    font-size: 9px;
}

/* Form Rows */
.api-form-row {
    margin-bottom: 15px;
}

.api-form-row label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #333;
    font-size: 14px;
}

.api-form-row input,
.api-form-row select,
.api-form-row textarea {
    width: 100%;
    padding: 10px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    transition: border-color 0.2s ease;
    box-sizing: border-box;
}

.api-form-row input:focus,
.api-form-row select:focus,
.api-form-row textarea:focus {
    outline: none;
    border-color: #1BA0D7;
}

/* Send Button */
.api-send-button {
    background: linear-gradient(135deg, #1BA0D7, #0D7AA7);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s ease;
}

.api-send-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(27, 160, 215, 0.3);
}

.api-send-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Response Section */
#sidebarResponseStatus {
    margin-bottom: 15px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
    border-left: 4px solid #28a745;
}

#sidebarResponseBody {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 15px;
    font-size: 12px;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'Monaco', 'Consolas', monospace;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.5rem;
        max-width: 100%;
    }
    
    .api-tool-floating-icon {
        width: 60px;
        height: 40px;
        right: 10px;
        top: 10px;
    }
    
    .api-text-line1 {
        font-size: 11px;
        color: white !important;
    }
    
    .api-text-line2 {
        font-size: 9px;
        color: white !important;
    }
}
</style>
""", unsafe_allow_html=True)

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
        # Get response from hybrid RAG system with conversation history
        response = chat(sanitized_input, conversation_history=st.session_state.messages)
    
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
