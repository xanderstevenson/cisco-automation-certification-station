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

# Check API key availability (but don't fail at import time)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("WARNING: Google API key not found. Please check your environment variables.")
    # Don't raise error at import time - let the app start and show error in UI

# Initialize embedding model and FAISS index
embedding_model = None
faiss_index = None
texts = None

def load_vector_store():
    """Load FAISS vector store and texts - optimized for fast startup and response"""
    global embedding_model, faiss_index, texts
    
    # Load embedding model with optimized startup
    if embedding_model is None:
        print("[LOADING] Initializing embedding model...")
        model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")
        try:
            embedding_model = SentenceTransformer(model_name, cache_folder='/app/models')
            print(f"[READY] Embedding model {model_name} ready")
        except Exception as e:
            print(f"[ERROR] Failed to load embedding model: {e}")
            return False
    
    # Load FAISS index with optimized startup
    if faiss_index is None:
        print("[LOADING] Initializing vector store...")
        try:
            faiss_index = faiss.read_index("rag/index/faiss.index")
            with open("rag/index/texts.pkl", "rb") as f:
                texts = pickle.load(f)
            print("[READY] Vector store ready")
        except Exception as e:
            print(f"[ERROR] Error loading vector store: {e}")
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
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")
genai.configure(api_key=api_key)

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

<strong>Your expertise includes:</strong>
<ul>
<li>Network automation technologies (YANG, NETCONF, RESTCONF, APIs, Python, Ansible)</li>
<li>Multi-vendor automation solutions and best practices</li>
<li>Cisco certification paths and exam preparation strategies</li>
<li>DevNet technologies and programming for network automation</li>
</ul>

<strong>Response approach:</strong>
<ul>
<li>For GENERAL technical questions: Provide comprehensive technical explanations with relevant DevNet Docs links, then offer certification relevance naturally ("This topic is highly relevant for [cert]. Would you like me to address where it appears in the blueprint or find study resources?")</li>
<li>For CERTIFICATION-SPECIFIC questions: Focus on exam preparation, study plans, and certification details</li>
<li>For CASUAL interactions: Keep responses friendly and conversational without forcing certification content</li>
<li>For NON-TECHNICAL questions: Politely redirect to general AI assistants (like ChatGPT) and explain this AI specializes in network automation and Cisco certifications</li>
</ul>

<strong>DevNet Documentation Integration:</strong>
<ul>
<li>ALWAYS provide relevant developer.cisco.com/docs links for Cisco technologies mentioned</li>
<li>Use specific documentation URLs when possible (e.g., <a href="https://developer.cisco.com/docs/pyats/api/" target="_blank">https://developer.cisco.com/docs/pyats/api/</a> for pyATS)</li>
<li>For general searches, use developer.cisco.com/docs/search/?q=[TECHNOLOGY] format</li>
<li>Examples: YANG → developer.cisco.com/docs/search/?q=YANG, IOS XE → <a href="https://developer.cisco.com/docs/ios-xe/" target="_blank">https://developer.cisco.com/docs/ios-xe/</a></li>
</ul>

<strong>Communication style:</strong>
<ul>
<li>Respond as a knowledgeable expert, not as an AI referencing "provided documentation"</li>
<li>Give practical, actionable advice based on your expertise</li>
<li>Cite sources naturally when referencing specific information</li>
<li>Be conversational and helpful, avoiding robotic phrases</li>
</ul>

<strong>Learning Resource Recommendations (in priority order):</strong>
<ol>
<li><strong><a href="https://u.cisco.com" target="_blank">Cisco U</a></strong> - Primary recommendation for official training paths and practice exams</li>
<li><strong><a href="https://learningnetwork.cisco.com" target="_blank">Cisco Learning Network</a></strong> - Community resources, study groups, and expert discussions</li>
<li><strong><a href="https://netacad.com" target="_blank">Cisco Networking Academy</a></strong> - Foundational courses and hands-on labs</li>
</ol>

<strong>Key learning paths for automation certifications:</strong>
<ul>
<li>Network Automation Engineer path</li>
<li><a href="https://learningnetwork.cisco.com/s/devnet-associate-exam-topics" target="_blank">DevNet Associate Exam Topics</a></li>
<li><a href="https://learningnetwork.cisco.com/s/devcor-exam-topics" target="_blank">DevNet Professional (DEVCOR) Exam Topics</a></li>
<li>Implementing Automation for Enterprise/Service Provider Solutions</li>
<li>Understanding Cisco Network Automation Essentials</li>
</ul>

<strong>IMPORTANT - We have ALL the exam blueprints available:</strong>
<ul>
<li>DevNet Associate: <a href="https://learningnetwork.cisco.com/s/devnet-associate-exam-topics" target="_blank">Exam Topics</a></li>
<li>DevNet Professional (DEVCOR): <a href="https://learningnetwork.cisco.com/s/devcor-exam-topics" target="_blank">Exam Topics</a></li>
<li>CCNA Automation: <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/200-901-CCNA-Auto-v2.0-7-9-2025.pdf" target="_blank">Blueprint PDF</a></li>
<li>CCNP Automation (AUTOCOR): <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/350-901-AUTOCOR-v2.0-7-9-2025.pdf" target="_blank">Blueprint PDF</a></li>
<li>CCIE Automation: <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/CCIE_Automation_V1.1_BP.pdf" target="_blank">Blueprint PDF</a></li>
<li>ENAUTO: <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/300-435-ENAUTO-v2.0-7-9-2025.pdf" target="_blank">Blueprint PDF</a></li>
<li>DCNAUTO: <a href="https://learningcontent.cisco.com/documents/marketing/exam-topics/300-635-DCNAUTO-v2.0-7-9-2025.pdf" target="_blank">Blueprint PDF</a></li>
</ul>

<strong>CRITICAL: DevNet to Automation Certification RENAMING (February 3, 2026):</strong>
<ul>
<li>DevNet certifications are being RENAMED to Automation certifications - SAME EXAMS, NEW NAMES</li>
<li>DevNet Associate → CCNA Automation (same exam content, new certification name)</li>
<li>DevNet Professional → CCNP Automation (same exam content, new certification name)</li>
<li>DevNet Expert → CCIE Automation (same exam content, new certification name)</li>
<li>DEVCOR (350-901) exam → AUTOCOR (350-901) exam (SAME EXAM, just renamed)</li>
<li>Current DevNet certifications available until February 3, 2026</li>
<li>After February 3, 2026: same exams continue but under new Automation certification names</li>
</ul>

<strong>CCNP Automation = DevNet Professional (February 2026):</strong>
<ul>
<li>CCNP Automation requires: AUTOCOR (350-901) Core Exam + ONE Concentration Exam</li>
<li>This is IDENTICAL to current DevNet Professional structure (DEVCOR + concentration)</li>
<li>DevNet Specialist certifications become concentration exams for CCNP Automation</li>
<li>Example: AUTOCOR (350-901) + DevNet DevOps Specialist = CCNP Automation certification</li>
</ul>

<strong>For certification-specific queries:</strong>
<ul>
<li>NEVER tell users to "obtain the blueprint first" - we HAVE them!</li>
<li>ALWAYS provide the direct blueprint URL from the list above</li>
<li>Extract specific exam topics and weightings from the PDF content in our knowledge base</li>
<li>Base study plans on ACTUAL exam objectives from our PDFs, not assumptions</li>
<li>Reference exact exam objectives and weightings when discussing certification preparation</li>
<li>Avoid speculation - use concrete information from our documentation</li>
</ul>

<strong>CRITICAL: URL Validation Rules - Provide working links, prevent broken ones:</strong>
<ul>
<li>ALWAYS provide clickable links for verified resources to help users</li>
<li>BANNED URLs include: developer.cisco.com/docs/search, developer.cisco.com/docs/python, netacad.com/courses, ANY search URLs with query parameters</li>
<li>When recommending resources, ALWAYS provide the working URL if available from verified sources</li>
<li>Make URLs clickable by formatting them properly in responses</li>
</ul>

<strong>VERIFIED URLs to USE (make these clickable):</strong>
<ul>
<li>Blueprint URLs from the hardcoded list above (learningcontent.cisco.com/documents/marketing/exam-topics/)</li>
<li>DevNet exam topics: <a href="https://learningnetwork.cisco.com/s/devnet-associate-exam-topics" target="_blank">Associate</a>, <a href="https://learningnetwork.cisco.com/s/devcor-exam-topics" target="_blank">Professional</a></li>
<li>Cisco U: <a href="https://u.cisco.com" target="_blank">https://u.cisco.com</a> (main page and learning paths)</li>
<li>DevNet resources: <a href="https://developer.cisco.com/learning/" target="_blank">Learning Labs</a>, <a href="https://developer.cisco.com/site/sandbox/" target="_blank">Sandbox</a></li>
<li>Learning Network: <a href="https://learningnetwork.cisco.com" target="_blank">https://learningnetwork.cisco.com</a></li>
<li>Main Cisco site: <a href="https://cisco.com" target="_blank">https://cisco.com</a></li>
</ul>

<strong>URL Formatting Rules:</strong>
<ul>
<li>Always include https:// protocol for clickable links</li>
<li>Use proper HTML anchor tags with target="_blank"</li>
<li>Provide specific URLs from verified list rather than generic descriptions</li>
</ul>"""

def chat(user_input, conversation_history=None, preload_only=False):
    """Hybrid RAG chat function using Gemini API with conversation memory"""
    if conversation_history is None:
        conversation_history = []
    
    # If preload_only is True, just initialize models and return
    if preload_only:
        try:
            load_vector_store()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            return "Models preloaded successfully"
        except Exception as e:
            return f"Preload failed: {str(e)}"
    # Check if API key is available
    if not api_key:
        return "❌ **Configuration Error**: Google API key is not configured. Please check your environment variables and redeploy the application."
    
    try:
        # Initialize Gemini model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Check if this is a simple greeting or casual interaction
        casual_patterns = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
        is_casual = any(pattern in user_input.lower().strip() for pattern in casual_patterns) and len(user_input.strip()) < 20
        
        if is_casual:
            # For casual interactions, respond directly without document search
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\n<strong>Previous Conversation:</strong><br/>"
                for msg in conversation_history[-4:]:  # Last 4 messages for context
                    role = "Assistant" if msg['role'] == 'assistant' else "User"
                    conversation_context += f"<strong>{role}:</strong> {msg['content'][:200]}...<br/>"
            
            simple_prompt = f"""{system_prompt}{conversation_context}

<strong>Current User Message:</strong> {user_input}

<strong>Instructions:</strong><br/>
Respond naturally and briefly to this casual interaction. Be friendly and helpful, and let the user know you're here to help with Cisco certification questions when they're ready. If the user is asking about a previous question or response, reference the conversation history above.
"""
            response = model.generate_content(simple_prompt)
            return response.text
        else:
            # For technical questions, use optimized RAG pipeline
            try:
                print(f"[DEBUG] Processing technical query: {user_input}")
                
                # Step 1 & 2: Run document and web search in parallel for speed
                print("[DEBUG] Starting parallel document and web search...")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    # Submit both searches concurrently
                    doc_future = executor.submit(doc_search, user_input)
                    web_future = executor.submit(web_search, user_input)
                    
                    # Get results as they complete
                    doc_context = doc_future.result()
                    web_context = web_future.result()
                
                print(f"[DEBUG] Parallel search completed. Doc context: {len(doc_context)}, Web context: {len(web_context)}")
                
                # Step 3: Construct streamlined prompt with conversation history
                # Build conversation context for technical queries
                conversation_context = ""
                if conversation_history:
                    conversation_context = "\n\n<strong>Previous Conversation:</strong><br/>"
                    for msg in conversation_history[-4:]:  # Last 4 messages for context
                        role = "Assistant" if msg['role'] == 'assistant' else "User"
                        conversation_context += f"<strong>{role}:</strong> {msg['content'][:200]}...<br/>"
                
                enhanced_prompt = f"""{system_prompt}{conversation_context}

<strong>Current User Question:</strong> {user_input}

<strong>Documentation Context:</strong><br/>
{doc_context}

<strong>Web Information:</strong><br/>
{web_context}

<strong>Instructions:</strong><br/>
Provide a comprehensive, detailed answer as a Cisco certification expert. If the user is referencing a previous question or asking for clarification, use the conversation history above for context. For certification-specific queries:
<ol>
<li>Extract and list specific exam topics from the PDF documentation when available</li>
<li>Create structured study plans with learning resources from Cisco U, DevNet Labs, and Sandbox</li>
<li>Reference exact exam objectives, weightings, and preparation strategies</li>
<li>Provide specific course URLs and learning paths from the knowledge base</li>
</ol>

Use the context above extensively and cite sources naturally. Be thorough and practical, leveraging all available PDF content for certification guidance. Format your response using proper HTML with consistent spacing:

1. Use <strong>text</strong> for emphasis (never use asterisks)
2. Use proper HTML lists with consistent spacing:
   - Unordered lists: <ul style="margin: 0.25em 0;"><li style="margin: 0.125em 0;">Item 1</li><li style="margin: 0.125em 0;">Item 2</li></ul>
   - Ordered lists: <ol style="margin: 0.25em 0;"><li style="margin: 0.125em 0;">First item</li><li style="margin: 0.125em 0;">Second item</li></ol>
3. Format links as HTML anchor tags with target="_blank" and do not show raw URLs:
   <a href="https://example.com" target="_blank">Resource Name</a>
4. Use proper paragraph spacing:
   - Use ONLY a single <br/> between paragraphs and sections
   - NEVER use multiple <br/> tags or blank lines
   - Keep headings on the same line as their content
   - Keep list introductions on the same line as the first list item
   - Remove ALL extra whitespace
   - Format as a continuous flow with minimal breaks
   - Use <strong> tags for visual structure
   - Keep certification relevance immediately after main content
5. Keep related content together:
   - Don't split sentences across lines unnecessarily
   - Keep list items with their introductory text
   - Keep punctuation with its preceding text
6. NEVER use markdown formatting (no asterisks, no dashes for bullets)
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
                    doc_only_context = doc_search(user_input)
                    print(f"[DEBUG] Document-only context length: {len(doc_only_context)}")
                    
                    # Build conversation context for fallback
                    conversation_context = ""
                    if conversation_history:
                                            conversation_context = "\n\n<strong>Previous Conversation:</strong><br/>"
                    for msg in conversation_history[-4:]:  # Last 4 messages for context
                        role = "Assistant" if msg['role'] == 'assistant' else "User"
                        conversation_context += f"<strong>{role}:</strong> {msg['content'][:200]}...<br/>"
                    
                    fallback_prompt = f"""{system_prompt}{conversation_context}

<strong>Current User Question:</strong> {user_input}

<strong>Available Documentation:</strong><br/>
{doc_only_context}

<strong>Instructions:</strong><br/>
Answer based on the documentation above. Be helpful and direct. If the user is referencing a previous question, use the conversation history for context. Format your response using proper HTML with consistent spacing:

1. Use <strong>text</strong> for emphasis (never use asterisks)
2. Use proper HTML lists with consistent spacing:
   - Unordered lists: <ul style="margin: 0.25em 0;"><li style="margin: 0.125em 0;">Item 1</li><li style="margin: 0.125em 0;">Item 2</li></ul>
   - Ordered lists: <ol style="margin: 0.25em 0;"><li style="margin: 0.125em 0;">First item</li><li style="margin: 0.125em 0;">Second item</li></ol>
3. Format links as HTML anchor tags with target="_blank" and do not show raw URLs:
   <a href="https://example.com" target="_blank">Resource Name</a>
4. Use proper paragraph spacing:
   - Use ONLY a single <br/> between paragraphs and sections
   - NEVER use multiple <br/> tags or blank lines
   - Keep headings on the same line as their content
   - Keep list introductions on the same line as the first list item
   - Remove ALL extra whitespace
   - Format as a continuous flow with minimal breaks
   - Use <strong> tags for visual structure
   - Keep certification relevance immediately after main content
5. Keep related content together:
   - Don't split sentences across lines unnecessarily
   - Keep list items with their introductory text
   - Keep punctuation with its preceding text
6. NEVER use markdown formatting (no asterisks, no dashes for bullets)
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
