import chainlit as cl
from hybrid_rag_gpt import search_docs, search_web, generate_answer

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content

    # Step 1: Search vector store
    docs = search_docs(user_query)

    # Step 2: Search web
    web = search_web(user_query)

    # Step 3: Generate final answer
    answer = generate_answer(user_query, docs, web)

    await cl.Message(content=answer).send()
