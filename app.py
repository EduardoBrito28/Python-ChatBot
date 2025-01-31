import streamlit as st
from utils import chatbot, text
from streamlit_chat import message
import os
import hashlib


def main():
    st.set_page_config(page_title="UBV Chatbot", page_icon=":books:")
    st.header("Converse com seus arquivos")
    user_question = st.text_input("Faça uma pergunta para mim!")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

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
            for pdf in pdf_docs:
                # Calcular o hash do arquivo
                pdf_hash = hashlib.md5(pdf.getvalue()).hexdigest()

                # Verificar se o hash já existe no banco de dados
                if text.document_exists(pdf_hash):
                    st.warning(
                        f"O arquivo '{pdf.name}' já foi carregado anteriormente."
                    )
                else:
                    # Definir o caminho completo para salvar o arquivo na subpasta
                    subpasta = os.path.join(os.getcwd(), "arquivos")
                    if not os.path.exists(subpasta):
                        os.makedirs(subpasta)
                    caminho_arquivo = os.path.join(subpasta, pdf.name)

                    # Salvar o arquivo PDF na subpasta 'arquivos'
                    with open(caminho_arquivo, "wb") as f:
                        f.write(pdf.getbuffer())

                    file_text = text.process_files([caminho_arquivo])
                    text.save_document_metadata(pdf.name, file_text, pdf_hash)
                    chunks = text.create_text_chunks(file_text)
                    vectorstore = chatbot.create_vectore(chunks)
                    st.session_state.conversation = chatbot.create_conversation_chain(
                        vectorstore
                    )

        if st.button("Ver Histórico"):
            history = chatbot.get_chat_history()
            for chat in history:
                st.write(f"**Pergunta:** {chat['question']}")
                st.write(f"**Resposta:** {chat['answer']}")


if __name__ == "__main__":
    main()
