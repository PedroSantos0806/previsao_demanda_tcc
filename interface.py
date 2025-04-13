import streamlit as st
import pandas as pd
from datetime import date, datetime
from database import session, Venda, Usuario
from model import carregar_dados, treinar_modelo, prever_demanda
from sqlalchemy.exc import IntegrityError
import hashlib
import plotly.express as px

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

# Login/Cadastro
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

# Sistema logado
else:
    st.sidebar.success(f"Logado como: {st.session_state.nome_usuario}")
    if st.sidebar.button("Sair"):
        del st.session_state.usuario_id
        del st.session_state.nome_usuario
        st.rerun()

    st.title("📈 Previsão de Demanda com Machine Learning")

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
        if st.form_submit_button("Cadastrar Venda"):
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

    df = carregar_dados(usuario_id=st.session_state.usuario_id)

    # Filtro por produto
    if not df.empty:
        produtos = df['produto'].unique()
        produto_escolhido = st.selectbox("🔍 Selecione o produto para previsão", produtos)
    else:
        st.info("Cadastre vendas para continuar.")
        st.stop()

    # Previsão de demanda
    st.markdown("## 🔮 Prever Demanda Futura")
    dias = st.slider("Número de dias para previsão", 1, 30, 7)

    if st.button("Prever Demanda"):
        modelo, ultimo_dia = treinar_modelo(df, produto_escolhido)
        previsoes = prever_demanda(modelo, ultimo_dia, dias)
        st.dataframe(previsoes, use_container_width=True)

        fig = px.line(previsoes, x='Data Prevista', y='Demanda Prevista',
                      title="📊 Gráfico de Previsão de Demanda",
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # Estatísticas
    st.markdown("## 📊 Estatísticas de Vendas")
    df['data'] = pd.to_datetime(df['data'])
    filtro_produto = df[df['produto'] == produto_escolhido]
    media_diaria = filtro_produto.groupby(df['data'].dt.date)['quantidade'].sum().mean()
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Média Diária", f"{media_diaria:.2f}")
    col2.metric("🔼 Máximo Vendido", filtro_produto['quantidade'].max())
    col3.metric("🔽 Mínimo Vendido", filtro_produto['quantidade'].min())

    # Histórico
    st.markdown("## 📜 Histórico de Vendas")
    st.dataframe(filtro_produto.sort_values(by="data"), use_container_width=True)

    # Comparar previsão com vendas passadas
    st.markdown("## 🔁 Verificar Previsão em Data Passada")
    data_analise = st.date_input("Selecione a data para verificar previsão")

    if st.button("Verificar Previsão da Época"):
        modelo, _ = treinar_modelo(df, produto_escolhido)
        dias_passados = (data_analise - df['data'].min()).days
        previsao = modelo.predict([[dias_passados]])[0]
        previsao = max(0, int(previsao))

        vendas_reais = filtro_produto[filtro_produto['data'].dt.date == data_analise]
        vendas_total = vendas_reais['quantidade'].sum()

        st.info(f"📆 Previsão para {data_analise}: **{previsao} unidades**")
        st.success(f"📦 Vendas reais nesse dia: **{vendas_total} unidades**")
