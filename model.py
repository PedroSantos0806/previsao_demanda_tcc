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
    df['data'] = pd.to_datetime(df['data'])
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
    previsoes = [max(0, int(p)) for p in previsoes]

    return pd.DataFrame({
        "Data Prevista": futuras_datas,
        "Demanda Prevista": previsoes
    })
