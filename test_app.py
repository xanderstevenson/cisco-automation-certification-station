#!/usr/bin/env python3
"""
Minimal test app to verify port switching works
"""

import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="🚀"
)

st.title("🎉 SUCCESS!")
st.write("Port switching works! The loading screen → Streamlit transition is working.")
st.write("Your custom loading screen successfully transitioned to this Streamlit app.")
st.success("Ready to deploy the full Cisco Automation Certification Station!")
