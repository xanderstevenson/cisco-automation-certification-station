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

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")

# Test prompt with HTML formatting requirements
test_prompt = """You are a Cisco certification expert. Format your response using proper HTML:
- Use <strong> for emphasis
- Use proper HTML lists (<ul>/<ol> with <li>)
- Format links as <a href="url" target="_blank">text</a>
- Use single <br/> for paragraph breaks

Question: What's the difference between CCNA Automation and DevNet Associate certifications?"""

try:
    # Generate response
    response = model.generate_content(test_prompt)
    print("\nTest Response:")
    print("-" * 80)
    print(response.text)
    print("-" * 80)
    print("\nGeneration succeeded!")
except Exception as e:
    print(f"\nError during generation: {str(e)}")
