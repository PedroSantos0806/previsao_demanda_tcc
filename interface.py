import streamlit as st
from datetime import date
from database import session, Venda
from model import carregar_dados, treinar_modelo, prever_demanda

st.set_page_config(page_title="Previsão de Demanda", layout="centered")
st.title("Previsão de Demanda com Machine Learning")

# Cadastrando vendas

st.header("Cadastrar nova Venda")
with st.form(key="form_venda"):
    data = st.date_input("Data da Venda", value=date.today())
    quantidade = st.number_input("Quantidade Vendida", min_value=1)
    produto = st.text_input("Produto (Opcional)")
    valor = st.number_input("Valor Total (Opcional)", step=0.01)
    enviar = st.form_submit_button("Cadastrar Venda")

    if enviar:
        nova_venda = Venda(data=data, quantidade=quantidade, produto=produto, valor=valor)
        session.add(nova_venda)
        session.commit()
        st.success("Venda cadastrada com sucesso!")


# Realizando previsão de demanda

st.header("Previsão de Demanda")
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
    