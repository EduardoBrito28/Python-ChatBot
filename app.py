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
                file_text = text.process_files([pdf])
                text.save_document_metadata(pdf.name, file_text)
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
