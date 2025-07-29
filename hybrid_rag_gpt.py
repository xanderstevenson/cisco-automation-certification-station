# hybrid_rag_gpt.py

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from rag.retriever import retrieve_answer, cleanup_memory
from serpapi import GoogleSearch

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))
model = genai.GenerativeModel('gemini-1.5-flash')

# Doc search tool using your improved retriever with lazy loading
def doc_search(query: str) -> str:
    # Reduce search results for faster response
    return retrieve_answer(query, k=2)

# Internet search fallback via SerpAPI
def web_search(query: str) -> str:
    # Skip web search if no API key to speed up response
    if not os.environ.get("SERPAPI_KEY"):
        return "Web search unavailable (no API key configured)."
    
    params = {
        "q": query,
        "api_key": os.environ.get("SERPAPI_KEY"),
        "engine": "google",
        "num": 2  # Reduced for faster response
    }
    try:
        results = GoogleSearch(params).get_dict()
        snippets = [r.get("snippet", "") for r in results.get("organic_results", [])[:2] if r.get("snippet")]
        return "\n".join(snippets) if snippets else "No internet results found."
    except Exception as e:
        return "Web search temporarily unavailable."

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
            # For technical questions, use optimized RAG pipeline
            try:
                # Step 1: Get relevant documents (reduced results)
                doc_context = doc_search(user_query)
                
                # Step 2: Get web search results (with fallback)
                web_context = web_search(user_query)
                
                # Step 3: Construct streamlined prompt
                enhanced_prompt = f"""{system_prompt}

**User Question:** {user_query}

**Documentation Context:**
{doc_context}

**Web Information:**
{web_context}

**Instructions:** 
Provide a concise, helpful answer as a Cisco certification expert. Use the context above and cite sources naturally. Keep responses focused and practical. If information is limited, acknowledge it while still being helpful.
"""
                
                # Step 4: Generate response with Gemini (with timeout handling)
                response = model.generate_content(
                    enhanced_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=800,  # Limit response length for speed
                        temperature=0.7
                    )
                )
                # Cleanup memory after processing
                cleanup_memory()
                return response.text
            
            except Exception as tech_error:
                # Fallback to document-only response if full pipeline fails
                try:
                    doc_only_context = doc_search(user_query)
                    fallback_prompt = f"""{system_prompt}

**User Question:** {user_query}

**Available Documentation:**
{doc_only_context}

**Instructions:** Answer based on the documentation above. Be helpful and direct.
"""
                    response = model.generate_content(fallback_prompt)
                    return response.text
                except:
                    return "I'm experiencing some technical difficulties. Please try asking your question again, or try a simpler version of your question."
        
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
