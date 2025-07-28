# hybrid_rag_gpt.py

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from rag.retriever import retrieve_answer
from serpapi import GoogleSearch

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))
model = genai.GenerativeModel('gemini-1.5-flash')

# Doc search tool using your improved retriever with lazy loading
def doc_search(query: str) -> str:
    return retrieve_answer(query)

# Internet search fallback via SerpAPI
def web_search(query: str) -> str:
    params = {
        "q": query,
        "api_key": os.environ.get("SERPAPI_KEY", ""),
        "engine": "google",
        "num": 3
    }
    try:
        results = GoogleSearch(params).get_dict()
        snippets = [r.get("snippet", "") for r in results.get("organic_results", []) if r.get("snippet")]
        return "\n".join(snippets) if snippets else "No internet results found."
    except Exception as e:
        return f"Error during internet search: {e}"

# System prompt for Gemini
system_prompt = (
    "You are a helpful AI assistant for Cisco network engineering certification preparation. "
    "You specialize in automation topics including CCNA Auto, ENAUTO, DCNAUTO, AUTOCOR, and CCIE Automation. "
    "\n\nFor casual greetings or simple interactions, respond naturally and briefly. "
    "For technical questions, provide comprehensive, accurate answers with practical examples. "
    "Only search through documentation and provide detailed responses when the user asks specific technical questions. "
    "Always cite your sources when referencing specific documentation or external information."
)

def chat(user_query):
    """Hybrid RAG chat function using Gemini API"""
    try:
        # Check if this is a simple greeting or casual interaction
        casual_patterns = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
        is_casual = any(pattern in user_query.lower().strip() for pattern in casual_patterns) and len(user_query.strip()) < 20
        
        if is_casual:
            # For casual interactions, respond directly without document search
            simple_prompt = f"""{system_prompt}

**User Message:** {user_query}

**Instructions:** 
Respond naturally and briefly to this casual interaction. Be friendly and helpful, and let the user know you're here to help with Cisco certification questions when they're ready.
"""
            response = model.generate_content(simple_prompt)
            return response.text
        else:
            # For technical questions, use full RAG pipeline
            # Step 1: Get relevant documents
            doc_context = doc_search(user_query)
            
            # Step 2: Get web search results for current info
            web_context = web_search(user_query)
            
            # Step 3: Construct enhanced prompt with context
            enhanced_prompt = f"""{system_prompt}

**User Question:** {user_query}

**Relevant Documentation Context:**
{doc_context}

**Current Web Information:**
{web_context}

**Instructions:** 
Answer the user's question in a natural, conversational tone as if you're a knowledgeable Cisco certification expert. 
Use the documentation and web information above to provide accurate, helpful answers.
When referencing sources, do so naturally (e.g., "According to Cisco's documentation..." or "Based on current information...").
Avoid robotic phrases like "The provided text states" - instead, speak naturally and directly to the user.

IMPORTANT: When recommending study resources, ALWAYS prioritize official Cisco resources:
- Cisco U (u.cisco.com)
- Cisco Learning Network (learningnetwork.cisco.com)
- Cisco NetAcad (netacad.com)
- Official Cisco certification pages
Provide actual clickable URLs when mentioning resources. Avoid recommending third-party sites unless specifically asked.

If you don't have complete information, be honest about it while still providing helpful guidance.
"""
            
            # Step 4: Generate response with Gemini
            response = model.generate_content(enhanced_prompt)
            return response.text
        
    except Exception as e:
        return f"Error generating response: {str(e)}. Please try again."

# For local testing
if __name__ == "__main__":
    while True:
        query = input("Ask your AI: ")
        print("\n---\n")
        answer = chat(query)
        print(answer)
        print("\n===\n")
