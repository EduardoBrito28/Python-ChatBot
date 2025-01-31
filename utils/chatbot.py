from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.retrievers import BaseRetriever
from utils import db

import os

# Definir a chave da API diretamente no código
os.environ["OPENAI_API_KEY"] = (
    "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"
)


def create_vectorstore_from_documents(documents):
    # Gere embeddings para os documentos
    embeddings = OpenAIEmbeddings()
    # Crie o índice vetorial usando FAISS
    vectorstore = FAISS.from_texts(texts=documents, embedding=embeddings)
    return vectorstore

def get_retriever_from_vectorstore(vectorstore) -> BaseRetriever:
    # Crie um retriever a partir do vectorstore
    retriever = vectorstore.as_retriever()
    return retriever


def retrieve_relevant_documents(query):
    # Recuperar documentos relevantes do MongoDB com base na consulta
    documents_cursor = db.documents_collection.find({"content": {"$regex": query, "$options": "i"}})
    documents = [doc['content'] for doc in documents_cursor]
    # Crie o vectorstore a partir dos documentos
    vectorstore = create_vectorstore_from_documents(documents)
    # Obtenha o retriever a partir do vectorstore
    retriever = get_retriever_from_vectorstore(vectorstore)
    return retriever


def generate_response(query, retriever):
    # Gerar resposta com base nos documentos relevantes
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory
    )
    response = conversation_chain.run(input=query)
    return response



def save_chat(question, answer):
    chat_entry = {"question": question, "answer": answer}
    db.chats_collection.insert_one(chat_entry)


def get_chat_history():
    return list(db.chats_collection.find({}, {"_id": 0}))
