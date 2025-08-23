import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('SERPAPI_KEY')
if not api_key:
    print("Error: SERPAPI_KEY not found in environment variables")
    exit(1)

# Test search
url = "https://google.serper.dev/search"
payload = json.dumps({
    "q": "What is network automation?",
    "gl": "us",
    "hl": "en"
})
headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    
    # Print the response
    print("=== SEARCH RESULTS ===")
    data = response.json()
    
    # Extract and print organic results
    if 'organic' in data:
        print("\n=== ORGANIC RESULTS ===")
        for i, result in enumerate(data['organic'][:3], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.get('title', 'No title')}")
            print(f"Link: {result.get('link', 'No link')}")
            print(f"Snippet: {result.get('snippet', 'No snippet')}")
    
    # Print answer box if available
    if 'answerBox' in data:
        print("\n=== ANSWER ===")
        print(data['answerBox'].get('snippet', 'No answer text'))
        
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
