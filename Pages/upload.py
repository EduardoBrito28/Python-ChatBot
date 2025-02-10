import streamlit as st
from utils import text, chatbot
import hashlib
import os
from streamlit_option_menu import option_menu


st.set_page_config(page_title="Upload de Arquivos", page_icon="📂")



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


pdf_docs = st.file_uploader(
    "Carregue os seus arquivos em formato PDF ou XLSX", accept_multiple_files=True
)
if st.button("Processar"):
    novos_arquivos = []
    for pdf in pdf_docs:
        pdf_hash = hashlib.md5(pdf.getvalue()).hexdigest()
        if text.document_exists(pdf_hash):
            st.warning(f"O arquivo '{pdf.name}' já foi carregado anteriormente.")
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
