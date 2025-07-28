import chainlit as cl
from hybrid_rag_gpt import chat

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content

    # Generate response using hybrid RAG with Gemini
    # This automatically searches docs, web, and generates the final answer
    answer = chat(user_query)

    await cl.Message(content=answer).send()
