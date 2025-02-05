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


def create_vector(chunks):
    embeddings = OpenAIEmbeddings()
    index_dir = "faiss_index"

    # Verificar se o diretório existe; caso contrário, criá-lo
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    # Caminho completo para o arquivo do índice
    index_path = os.path.join(index_dir, "index.faiss")

    # Verificar se o arquivo de índice existe
    if os.path.exists(index_path):
        # Carregar o índice existente
        vectorstore = FAISS.load_local(
            index_dir, embeddings=embeddings, allow_dangerous_deserialization=True
        )
    else:
        # Criar um novo índice
        vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    # Adicionar novos textos ao índice
    vectorstore.add_texts(texts=chunks)

    # Salvar o índice atualizado
    vectorstore.save_local(index_dir)

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
