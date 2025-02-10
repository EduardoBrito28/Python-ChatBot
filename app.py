import streamlit as st
from utils import chatbot, text
from streamlit_chat import message
import os
import hashlib
from pymongo import MongoClient

# Verifica se o usuário está autenticado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.switch_page("Pages/login.py")

st.set_page_config(page_title="UBV Chatbot", page_icon=":books:")


st.header(f"Bem-vindo, {st.session_state.username}")


def load_stored_documents(uploaded_files=None):
    """Carrega documentos armazenados localmente na pasta 'arquivos' e os processa para o chatbot."""
    file_text = ""
    if uploaded_files:
        # Processa os arquivos carregados pelo usuário
        file_text = text.process_files(uploaded_files)
    else:
        # Processa os arquivos já armazenados localmente
        subpasta = os.path.join(os.getcwd(), "arquivos")
        for filename in os.listdir(subpasta):
            caminho_arquivo = os.path.join(subpasta, filename)
            if filename.endswith(".pdf") or filename.endswith(".xlsx"):
                with open(caminho_arquivo, "rb") as f:
                    file_text += text.process_files([f])

    if file_text:
        chunks = text.create_text_chunks(file_text)
        vectorstore = chatbot.create_vector(chunks)
        return chatbot.create_conversation_chain(vectorstore)
    else:
        return None


def main():
    if "conversation" not in st.session_state:
        st.session_state.conversation = load_stored_documents()

    user_question = st.text_input("Faça uma pergunta para mim!")

    if user_question:
        response = st.session_state.conversation(user_question)["chat_history"]
        for i, text_message in enumerate(response):
            message(text_message.content, is_user=(i % 2 == 0), key=str(i) + "_user")
        # Salvar a pergunta e a resposta no MongoDB
        if response:
            chatbot.save_chat(user_question, response[-1].content)


if __name__ == "__main__":
    main()
