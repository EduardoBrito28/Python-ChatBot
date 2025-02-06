import streamlit as st
from utils.db import get_user
from utils.auth import check_password

st.set_page_config(page_title="Login", page_icon="🔑")

st.title("Login")

# Formulário de login
with st.form("login_form"):
    email = st.text_input("E-mail")
    password = st.text_input("Senha", type="password")
    submitted = st.form_submit_button("Entrar")

    if submitted:
        user = get_user(email)
        if user and check_password(password, user["senha"]):
            st.session_state.logged_in = True
            st.session_state.username = user["nome"]
            st.session_state.user_email = user["email"]
            st.success("Login bem-sucedido! Redirecionando...")
            st.rerun()
        else:
            st.error("E-mail ou senha incorretos.")

# Redireciona caso já esteja logado
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.switch_page("app.py")
