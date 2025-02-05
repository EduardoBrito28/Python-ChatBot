import streamlit as st
from utils import chatbot, text
from streamlit_chat import message
import os
import hashlib


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
    st.set_page_config(page_title="UBV Chatbot", page_icon=":books:")
    st.header("Converse com seus arquivos")

    if "conversation" not in st.session_state:
        st.session_state.conversation = load_stored_documents()

    # Permitir o upload de múltiplos arquivos
    uploaded_files = st.file_uploader(
        "Carregue seus arquivos PDF ou Excel",
        type=["pdf", "xlsx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        # Processar os arquivos carregados
        conversation = load_stored_documents(uploaded_files)
        st.session_state.conversation = conversation
        st.success("Arquivos processados e adicionados!")

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

        if st.button("Ver Histórico"):
            history = chatbot.get_chat_history()
            for chat in history:
                st.write(f"**Pergunta:** {chat['question']}")
                st.write(f"**Resposta:** {chat['answer']}")


if __name__ == "__main__":
    main()
