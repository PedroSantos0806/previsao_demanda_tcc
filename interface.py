import streamlit as st
import pandas as pd
from datetime import date
from database import session, Venda, Usuario
from model import carregar_dados, treinar_modelo, prever_demanda
from sqlalchemy.exc import IntegrityError
import hashlib

st.set_page_config(page_title="Previsão de Demanda", layout="centered")

# Funções auxiliares
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def autenticar(email, senha):
    senha_hash = hash_senha(senha)
    usuario = session.query(Usuario).filter_by(email=email, senha=senha_hash).first()
    return usuario

def cadastrar_usuario(nome, email, senha):
    senha_hash = hash_senha(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
    session.add(novo_usuario)
    try:
        session.commit()
        return True, "Usuário cadastrado com sucesso."
    except IntegrityError:
        session.rollback()
        return False, "Email já cadastrado."

# Login e Cadastro
if "usuario_id" not in st.session_state:
    aba = st.sidebar.radio("Acesso", ["Login", "Cadastrar"])

    if aba == "Login":
        st.title("Login")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            usuario = autenticar(email, senha)
            if usuario:
                st.session_state.usuario_id = usuario.id
                st.session_state.nome_usuario = usuario.nome
                st.rerun()
            else:
                st.error("Email ou senha inválidos.")

    else:
        st.title("Cadastrar Novo Usuário")
        nome = st.text_input("Nome Completo")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar"):
            sucesso, mensagem = cadastrar_usuario(nome, email, senha)
            if sucesso:
                st.success(mensagem)
            else:
                st.error(mensagem)

else:
    st.sidebar.success(f"Logado como: {st.session_state.nome_usuario}")
    if st.sidebar.button("Sair"):
        del st.session_state.usuario_id
        del st.session_state.nome_usuario
        st.rerun()

    st.title("Previsão de Demanda com Machine Learning")

    # Cadastro de vendas
    st.markdown("## 🛒 Cadastrar Nova Venda")
    with st.form(key="form_venda"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data da Venda", value=date.today())
            quantidade = st.number_input("Quantidade Vendida", min_value=1)
        with col2:
            produto = st.text_input("Nome do Produto")
            valor = st.number_input("Valor Total (R$)", min_value=0.01, format="%.2f")

        enviar = st.form_submit_button("Cadastrar Venda")
        if enviar:
            if not produto.strip():
                st.error("O nome do produto é obrigatório.")
            else:
                nova_venda = Venda(
                    data=data,
                    quantidade=quantidade,
                    produto=produto,
                    valor=valor,
                    usuario_id=st.session_state.usuario_id
                )
                session.add(nova_venda)
                session.commit()
                st.success("✅ Venda cadastrada com sucesso!")

    # Previsão de demanda
    st.markdown("## 📈 Previsão de Demanda com IA")
    st.markdown("Use o modelo de regressão linear para prever as vendas dos próximos dias.")
    dias = st.slider("Número de dias para previsão", min_value=1, max_value=30, value=7)

    if st.button("Prever Demanda"):
        df = carregar_dados(usuario_id=st.session_state.usuario_id)
    if df.empty:
        st.warning("Nenhum dado encontrado para previsão.")
    else:
        df['data'] = pd.to_datetime(df['data'])  # <-- Coloque aqui dentro
        modelo, ultimo_dia = treinar_modelo(df)
        previsoes = prever_demanda(modelo, ultimo_dia, dias)

        media_diaria = df.groupby(df['data'].dt.date)['quantidade'].sum().mean()
        max_vendas = df['quantidade'].max()
        min_vendas = df['quantidade'].min()

        st.subheader("Previsões de Demanda")
        st.dataframe(previsoes)

        st.markdown("### 📊 Estatísticas de Vendas")
        col1, col2, col3 = st.columns(3)
        col1.metric("📅 Média Diária", f"{media_diaria:.2f}")
        col2.metric("🔼 Máximo Vendido", f"{max_vendas}")
        col3.metric("🔽 Mínimo Vendido", f"{min_vendas}")

    # Histórico de vendas
    st.markdown("## 🧾 Histórico de Vendas")
    df = carregar_dados(usuario_id=st.session_state.usuario_id)
    if not df.empty:
        st.dataframe(df.sort_values(by="data"))
    else:
        st.info("Você ainda não cadastrou nenhuma venda.")