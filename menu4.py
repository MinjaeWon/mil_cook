# import streamlit as st

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


def get_conversation_chain(vetorestore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vetorestore.as_retriever(search_type='mmr', verbose=True),
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain


