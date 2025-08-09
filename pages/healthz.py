
# Health check endpoint for Streamlit
import streamlit as st

# Hide all Streamlit elements
hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stApp {display: none;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Just return a simple 200 OK
st.write("OK")
                