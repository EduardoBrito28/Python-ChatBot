import streamlit as st
from utils.db import create_user
from utils.auth import hash_password

st.set_page_config(page_title="Cadastro de Usuário", page_icon="📝")

st.title("Cadastro de Usuário")

# Formulário de cadastro
with st.form("register_form"):
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    departamento = st.text_input("Departamento")
    empresa = st.text_input("Empresa")
    senha = st.text_input("Senha", type="password")
    nivel_acesso = st.selectbox("Nível de Acesso", ["Usuário", "Administrador"])

    submitted = st.form_submit_button("Cadastrar")

    if submitted:
        if nome and email and senha:
            if create_user(nome, email, departamento, empresa, hash_password(senha), nivel_acesso):
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar. Tente outro e-mail.")
        else:
            st.warning("Preencha todos os campos.")

# Link para login
st.markdown("[Já tem uma conta? Faça login](login)")
