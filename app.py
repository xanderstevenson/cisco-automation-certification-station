import chainlit as cl
from hybrid_rag_gpt import chat

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content

    # Show professional thinking indicator for better UX during processing
    thinking_msg = cl.Message(content="⚡ Searching Cisco documentation and generating comprehensive response...")
    await thinking_msg.send()

    # Generate response using hybrid RAG with Gemini
    # This automatically searches docs, web, and generates the final answer
    answer = chat(user_query)

    # Remove thinking indicator and send final response
    await thinking_msg.remove()
    await cl.Message(content=answer).send()
