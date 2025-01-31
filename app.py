import streamlit as st
from utils import chatbot, text
from streamlit_chat import message

def main():
    st.set_page_config(page_title="UBV Chatbot", page_icon=":books:")
    st.header("Converse com seus arquivos")
    user_question = st.text_input("Faça uma pergunta para mim!")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if user_question:
        # Recuperar documentos relevantes do MongoDB
        relevant_documents = chatbot.retrieve_relevant_documents(user_question)
        # Gerar resposta com base nos documentos relevantes
        response = chatbot.generate_response(user_question, relevant_documents)
        if response:
            message(response, is_user=False)
            # Salvar a pergunta e a resposta no MongoDB
            chatbot.save_chat(user_question, response)
        else:
            st.warning("Nenhuma resposta foi gerada para a sua pergunta.")

    with st.sidebar:
        st.subheader("Seus arquivos")
        pdf_docs = st.file_uploader(
            "Carregue os seus arquivos em formato PDF", accept_multiple_files=True
        )

        if st.button("Processar"):
            for pdf in pdf_docs:
                file_hash = text.generate_file_hash(pdf)
                if text.document_exists(file_hash):
                    st.warning(f"O arquivo {pdf.name} já existe no banco de dados.")
                    continue

                file_text = text.process_files([pdf])
                text.save_document_metadata(pdf.name, file_text, file_hash)
                chunks = text.create_text_chunks(file_text)
                vectorstore = chatbot.create_vectorstore_from_documents(chunks)
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
