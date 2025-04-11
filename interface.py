import streamlit as st
from datetime import date
from database import session, Venda
from model import carregar_dados, treinar_modelo, prever_demanda

st.set_page_config(page_title="Previsão de Demanda", layout="centered")
st.title("Previsão de Demanda com Machine Learning")

if "usuario_id" not in st.session_state:
    st.header("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        from database import session, Usuario
        user = session.query(Usuario).filter_by(email=email, senha=senha).first()
        if user:
            st.session_state.usuario_id = user.id
            st.success("Login realizado com sucesso.")
        else:
            st.error("Email ou senha inválidos.")
    st.stop()

# Cadastrando vendas

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
            nova_venda = Venda(data=data, quantidade=quantidade, produto=produto, valor=valor, usuario_id=st.session_state.usuario_id)
            session.add(nova_venda)
            session.commit()
            st.success("✅ Venda cadastrada com sucesso!")

# Realizando previsão de demanda

st.image("https://cdn-icons-png.flaticon.com/512/3105/3105783.png", width=80)
st.markdown("## 📈 Previsão de Demanda com IA")
st.markdown("Use o modelo de regressão linear para prever as vendas dos próximos dias.")

dias = st.slider("Número de dias para previsão", min_value=1, max_value=30, value=7)

if st.button("Prever Demanda"):
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhum dado encontrado para previsão.")
    else:
        modelo, ultimo_dia = treinar_modelo(df)
        previsoes = prever_demanda(modelo, ultimo_dia, dias)
        st.subheader("Previsões de Demanda")
        st.dataframe(previsoes)


# visualização dos dados

st.header("Histórico de Vendas")
df = carregar_dados()
if not df.empty:
    st.dataframe(df.sort_values(by="data"))
df = df[df['usuario_id'] == st.session_state.usuario_id]
    