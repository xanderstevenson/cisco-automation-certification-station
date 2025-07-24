# hybrid_rag_gpt.py

import os
from openai import OpenAI
from rag.retriever import retrieve_answer
from serpapi import GoogleSearch

oai_client = OpenAI()

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

# Tools GPT can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "doc_search",
            "description": "Searches private documents for answers to a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Uses web search to retrieve recent or general info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            },
        },
    },
]

system_prompt = (
    "You are a helpful AI assistant for network engineering certification prep. "
    "You have access to private documents through 'doc_search' and internet via 'web_search'. "
    "Use both to provide the best answer. Combine facts from documents, internet, and your own knowledge. Cite sources."
)

def chat(user_query):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]

    response = oai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    first_response = response.choices[0].message

    if first_response.tool_calls:
        tool_outputs = []
        for call in first_response.tool_calls:
            query = eval(call.function.arguments)["query"]
            if call.function.name == "doc_search":
                tool_output = doc_search(query)
            elif call.function.name == "web_search":
                tool_output = web_search(query)
            else:
                tool_output = "Unknown tool called."

            tool_outputs.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": tool_output,
            })

        # Append tool responses and retry
        messages.append(first_response)
        messages.extend(tool_outputs)

        second_response = oai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return second_response.choices[0].message.content

    return first_response.content

# For local testing
if __name__ == "__main__":
    while True:
        query = input("Ask your AI: ")
        print("\n---\n")
        answer = chat(query)
        print(answer)
        print("\n===\n")
