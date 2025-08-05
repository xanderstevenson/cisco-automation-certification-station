# hybrid_rag_gpt.py

import os
import google.generativeai as genai
from dotenv import load_dotenv
from serpapi import GoogleSearch
import gc
import concurrent.futures
import threading
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()

# Ensure API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: Google API key not found. Please check your environment variables.")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Initialize embedding model and FAISS index
embedding_model = None
faiss_index = None
texts = None

def load_vector_store():
    """Load FAISS vector store and texts"""
    global embedding_model, faiss_index, texts
    if embedding_model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")
        embedding_model = SentenceTransformer(model_name)
    
    if faiss_index is None:
        try:
            faiss_index = faiss.read_index("rag/index/faiss.index")
            with open("rag/index/texts.pkl", "rb") as f:
                texts = pickle.load(f)
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    return True

def retrieve_answer(query: str, k: int = 5) -> str:
    """Retrieve relevant documents for the query"""
    if not load_vector_store():
        return "Error: Could not load document index."
    
    try:
        # Encode query
        query_embedding = embedding_model.encode([query])
        
        # Search FAISS index
        distances, indices = faiss_index.search(query_embedding, k)
        
        # Get relevant texts
        relevant_texts = []
        for idx in indices[0]:
            if idx < len(texts):
                relevant_texts.append(texts[idx])
        
        return "\n\n".join(relevant_texts)
    except Exception as e:
        print(f"Error in retrieve_answer: {e}")
        return "Error retrieving documents."

def cleanup_memory():
    """Clean up memory after processing"""
    gc.collect()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use Gemini 1.5 Flash for faster responses (optimized for speed)
model = genai.GenerativeModel("gemini-1.5-flash")

# Optimized generation config for comprehensive responses with good speed
fast_generation_config = genai.types.GenerationConfig(
    max_output_tokens=1500,  # Increased for comprehensive certification responses
    temperature=0.4,  # Lower for faster, more focused responses
    top_p=0.8,  # Slightly reduced for speed
    top_k=30  # Reduced for faster token selection
)

# Doc search tool using your improved retriever with lazy loading
def doc_search(query: str) -> str:
    # Increase search results for comprehensive certification information
    return retrieve_answer(query, k=5)

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
system_prompt = """You are a knowledgeable network automation expert who also provides Cisco certification guidance when relevant.

**Your expertise includes:**
- Network automation technologies (YANG, NETCONF, RESTCONF, APIs, Python, Ansible)
- Multi-vendor automation solutions and best practices
- Cisco certification paths and exam preparation strategies
- DevNet technologies and programming for network automation

**Response approach:**
- For GENERAL technical questions: Provide comprehensive technical explanations first, then briefly mention Cisco certification relevance if applicable
- For CERTIFICATION-SPECIFIC questions: Focus on exam preparation, study plans, and certification details
- For CASUAL interactions: Keep responses friendly and conversational without forcing certification content
- For NON-TECHNICAL questions: Politely redirect to general AI assistants (like ChatGPT) and explain this AI specializes in network automation and Cisco certifications

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

**IMPORTANT - We have ALL the exam blueprints available:**
- CCNA Automation: https://learningcontent.cisco.com/documents/marketing/exam-topics/200-901-CCNA-Auto-v2.0-7-9-2025.pdf
- CCNP Automation (AUTOCOR): https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf
- CCIE Automation: https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf
- ENAUTO: https://learningcontent.cisco.com/documents/marketing/exam-topics/300-435-ENAUTO-v2.0-7-9-2025.pdf
- DCNAUTO: https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf

**CRITICAL: Factual Accuracy Requirements:**
- February 3, 2026 is when DevNet certifications EVOLVE INTO the new Automation track (CCNA/CCNP/CCIE Automation)
- The new Automation certifications (CCNA Automation, CCNP Automation, CCIE Automation) LAUNCH February 3, 2026
- Current DevNet certifications are available until February 3, 2026
- New Automation certification blueprints will be available closer to the February 2026 launch date
- Base answers on actual PDF content from our knowledge base, not speculation

**For certification-specific queries:**
- NEVER tell users to "obtain the blueprint first" - we HAVE them!
- ALWAYS provide the direct blueprint URL from the list above
- Extract specific exam topics and weightings from the PDF content in our knowledge base
- Base study plans on ACTUAL exam objectives from our PDFs, not assumptions
- Reference exact exam objectives and weightings when discussing certification preparation
- Avoid speculation - use concrete information from our documentation

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
                
                # Step 1 & 2: Run document and web search in parallel for speed
                print("[DEBUG] Starting parallel document and web search...")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    # Submit both searches concurrently
                    doc_future = executor.submit(doc_search, user_query)
                    web_future = executor.submit(web_search, user_query)
                    
                    # Get results as they complete
                    doc_context = doc_future.result()
                    web_context = web_future.result()
                
                print(f"[DEBUG] Parallel search completed. Doc context: {len(doc_context)}, Web context: {len(web_context)}")
                
                # Step 3: Construct streamlined prompt
                enhanced_prompt = f"""{system_prompt}

**User Question:** {user_query}

**Documentation Context:**
{doc_context}

**Web Information:**
{web_context}

**Instructions:** 
Provide a comprehensive, detailed answer as a Cisco certification expert. For certification-specific queries:
1. Extract and list specific exam topics from the PDF documentation when available
2. Create structured study plans with learning resources from Cisco U, DevNet Labs, and Sandbox
3. Reference exact exam objectives, weightings, and preparation strategies
4. Provide specific course URLs and learning paths from the knowledge base

Use the context above extensively and cite sources naturally. Be thorough and practical, leveraging all available PDF content for certification guidance.
"""
                
                # Step 4: Generate response with Gemini (with timeout handling)
                print("[DEBUG] Generating response with Gemini...")
                response = model.generate_content(
                    enhanced_prompt,
                    generation_config=fast_generation_config
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
