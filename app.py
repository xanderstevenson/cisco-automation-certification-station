import chainlit as cl
from rag.retriever import retrieve_answer

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content
    answer = retrieve_answer(user_query)
    await cl.Message(content=answer).send()
