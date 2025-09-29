#!/usr/bin/env python3
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")

genai.configure(api_key=api_key)

# List available models
for m in genai.list_models():
    print(f"Name: {m.name}")
    print(f"Display Name: {m.display_name}")
    print(f"Description: {m.description}")
    print(f"Generation Methods: {m.supported_generation_methods}")
    print("-" * 80)
