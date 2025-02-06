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

# Menu superior
st.markdown(
    """
    <style>
        .topnav {
            background-color: #333;
            overflow: hidden;
            padding: 10px;
            width: 100%;
        }
        .topnav a {
            float: left;
            color: white;
            text-align: center;
            padding: 10px 15px;
            text-decoration: none;
            font-size: 17px;
        }
        .topnav a:hover {
            background-color: #ddd;
            color: black;
        }
    </style>
    <div class="topnav">
        <a href="app.py">Home</a>
        <a href="register">Cadastro de Usuários</a>
        <a href="login" onclick="window.location.reload();">Logout</a>
    </div>
""",
    unsafe_allow_html=True,
)

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

    with st.sidebar:
        st.subheader("Seus arquivos")
        pdf_docs = st.file_uploader(
            "Carregue os seus arquivos em formato PDF", accept_multiple_files=True
        )

        if st.button("Processar"):
            novos_arquivos = []
            for pdf in pdf_docs:
                pdf_hash = hashlib.md5(pdf.getvalue()).hexdigest()

                if text.document_exists(pdf_hash):
                    st.warning(
                        f"O arquivo '{pdf.name}' já foi carregado anteriormente."
                    )
                else:
                    subpasta = os.path.join(os.getcwd(), "arquivos")
                    caminho_arquivo = os.path.join(subpasta, pdf.name)

                    with open(caminho_arquivo, "wb") as f:
                        f.write(pdf.getbuffer())

                    novos_arquivos.append(caminho_arquivo)

                    file_text = text.process_files([caminho_arquivo])
                    text.save_document_metadata(pdf.name, file_text, pdf_hash)

            if novos_arquivos:
                st.session_state.conversation = load_stored_documents()
                st.success("Novos arquivos processados e adicionados!")


if __name__ == "__main__":
    main()
