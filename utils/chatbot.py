from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from utils import db

import os

# Definir a chave da API diretamente no código
os.environ["OPENAI_API_KEY"] = (
    "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"
)


def create_vectore(chunk):
    embaddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=chunk, embedding=embaddings)
    return vectorstore


def create_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


def save_chat(question, answer):
    chat_entry = {"question": question, "answer": answer}
    db.chats_collection.insert_one(chat_entry)


def get_chat_history():
    return list(db.chats_collection.find({}, {"_id": 0}))
