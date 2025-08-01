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
system_prompt = """You are a knowledgeable Cisco network automation expert and certification advisor. You help professionals prepare for Cisco automation certifications including CCNA Auto, ENAUTO, DCNAUTO, AUTOCOR, CCIE, and the upcoming CCNA Automation exam.

**Your expertise includes:**
- Network automation technologies (YANG, NETCONF, RESTCONF, APIs)
- Cisco certification paths and exam preparation strategies
- DevNet technologies and programming for network automation
- Multi-vendor automation solutions and best practices

**Communication style:**
- Respond as a knowledgeable expert, not as an AI referencing "provided documentation"
- Give practical, actionable advice based on your expertise
- Cite sources naturally when referencing specific information
- Be conversational and helpful, avoiding robotic phrases

**Learning Resource Recommendations (in priority order):**
1. **Cisco U (u.cisco.com)** - Primary recommendation for official training paths and practice exams
2. **Cisco Learning Network** - Community resources, study groups, and expert discussions  
3. **Cisco Networking Academy** - Foundational courses and hands-on labs

**Key learning paths for automation certifications:**
- Network Automation Engineer path
- Developing Applications Using Cisco Core Platforms APIs
- Implementing Automation for Enterprise/Service Provider Solutions
- Understanding Cisco Network Automation Essentials

Always provide specific, clickable URLs when recommending resources. Focus on official Cisco materials and avoid third-party recommendations unless specifically relevant."""

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
                print(f"[DEBUG] Processing technical query: {user_query}")
                
                # Step 1: Get relevant documents (reduced results)
                print("[DEBUG] Starting document search...")
                doc_context = doc_search(user_query)
                print(f"[DEBUG] Document search completed. Context length: {len(doc_context)}")
                
                # Step 2: Get web search results (with fallback)
                print("[DEBUG] Starting web search...")
                web_context = web_search(user_query)
                print(f"[DEBUG] Web search completed. Context length: {len(web_context)}")
                
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
                print("[DEBUG] Generating response with Gemini...")
                response = model.generate_content(
                    enhanced_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=800,  # Limit response length for speed
                        temperature=0.7
                    )
                )
                print("[DEBUG] Response generated successfully")
                
                # Cleanup memory after processing
                cleanup_memory()
                return response.text
            
            except Exception as tech_error:
                print(f"[ERROR] Technical query failed: {str(tech_error)}")
                print(f"[ERROR] Error type: {type(tech_error).__name__}")
                import traceback
                print(f"[ERROR] Full traceback: {traceback.format_exc()}")
                
                # Fallback to document-only response if full pipeline fails
                try:
                    print("[DEBUG] Attempting document-only fallback...")
                    doc_only_context = doc_search(user_query)
                    print(f"[DEBUG] Document-only context length: {len(doc_only_context)}")
                    
                    fallback_prompt = f"""{system_prompt}

**User Question:** {user_query}

**Available Documentation:**
{doc_only_context}

**Instructions:** Answer based on the documentation above. Be helpful and direct.
"""
                    response = model.generate_content(fallback_prompt)
                    return response.text
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback also failed: {str(fallback_error)}")
                    print(f"[ERROR] Fallback error type: {type(fallback_error).__name__}")
                    return f"Debug info - Technical error: {str(tech_error)}, Fallback error: {str(fallback_error)}"
        
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
