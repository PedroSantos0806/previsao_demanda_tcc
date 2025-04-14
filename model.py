import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from database import session, Venda
from datetime import timedelta

def carregar_dados(usuario_id):
    vendas = session.query(Venda).filter_by(usuario_id=usuario_id).all()
    dados = [{
        "data": venda.data,
        "produto": venda.produto,
        "quantidade": venda.quantidade,
        "valor": venda.valor
    } for venda in vendas]
    return pd.DataFrame(dados)

def treinar_modelo(df, produto=None):
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna(subset=['data', 'quantidade'])
    if produto:
        df = df[df['produto'] == produto]

    df = df.groupby('data').agg({'quantidade': 'sum'}).reset_index()
    df = df.sort_values('data')
    df['dias'] = (df['data'] - df['data'].min()).dt.days

    X = df[['dias']]
    y = df['quantidade']

    modelo = LinearRegression()
    modelo.fit(X, y)
    ultimo_dia = df['data'].max()
    return modelo, ultimo_dia

def prever_demanda(modelo, df, ultimo_dia, dias=7):
    futuras_datas = [ultimo_dia + timedelta(days=i+1) for i in range(dias)]
    dias_futuros = np.array([(d - df['data'].min()).days for d in futuras_datas]).reshape(-1, 1)
    previsoes = modelo.predict(dias_futuros)
    previsoes = [max(0, int(round(p))) for p in previsoes]
    return pd.DataFrame({"Data Prevista": futuras_datas, "Demanda Prevista": previsoes})

def treinar_multiplos_modelos(df, dias_futuros):
    resultados = []
    df['data'] = pd.to_datetime(df['data'])

    for produto in df['produto'].unique():
        dados_produto = df[df['produto'] == produto].copy()
        dados_produto = dados_produto.groupby(dados_produto['data'].dt.date)['quantidade'].sum().reset_index()
        dados_produto.columns = ['data', 'quantidade']
        dados_produto['dias'] = (pd.to_datetime(dados_produto['data']) - pd.to_datetime(dados_produto['data']).min()).dt.days

        if len(dados_produto) < 2:
            continue  # pula se não houver dados suficientes para o modelo

        modelo = LinearRegression()
        modelo.fit(dados_produto[['dias']], dados_produto['quantidade'])

        ultimo_dia = dados_produto['dias'].max()
        for i in range(1, dias_futuros + 1):
            dia_futuro = ultimo_dia + i
            data_prevista = pd.to_datetime(dados_produto['data'].min()) + pd.Timedelta(days=dia_futuro)
            demanda_prevista = max(0, int(modelo.predict([[dia_futuro]])[0]))

            resultados.append({
                "Produto": produto,
                "Data Prevista": data_prevista.date(),
                "Demanda Prevista": demanda_prevista
            })

    if not resultados:
        raise ValueError("Nenhum produto possui dados suficientes para previsão.")

    return pd.DataFrame(resultados)