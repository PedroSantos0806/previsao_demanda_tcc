import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from database import session, Venda
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor

def carregar_dados(usuario_id):
    vendas = session.query(Venda).filter_by(usuario_id=usuario_id).all()
    dados = [{
        "data": venda.data,
        "produto": venda.produto,
        "quantidade": venda.quantidade,
        "valor": venda.valor
    } for venda in vendas]
    return pd.DataFrame(dados)

def preprocessar_dados(df, produto=None):
    df = df.copy()
    df['data'] = pd.to_datetime(df['data'])
    if produto:
        df = df[df['produto'] == produto]
    
    df = df.groupby('data').agg({'quantidade': 'sum'}).reset_index()
    df = df.sort_values(by="data")
    df["dias"] = (df["data"] - df["data"].min()).dt.days
    return df

def treinar_modelo(df, produto=None):
    df - preprocessar_dados(df, produto)
    if len(df) < 2:
        raise ValueError("Dados insuficientes para treinar o modelo.")
    
    x = df[['dias']]
    y = df['quantidade']

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(x, y)
    r2 = modelo.score(x, y)
    ultimo_dia = df['data'].max()

    return modelo, ultimo_dia, r2

def prever_demanda(modelo, df, produto, ultimo_dia, dias=7):
    df = preprocessar_dados(df, produto)
    futuras_datas = [ultimo_dia + timedelta(days=i+1) for i in range(dias)]
    dias_futuros = np.array([(d - df['data'].min()).days for d in futuras_datas]).reshape(-1, 1)
    previsoes = modelo.predict(dias_futuros)
    previsoes = [max(0, round(p, 2)) for p in previsoes]

    return pd.DataFrame({"Data Prevista": futuras_datas, "Demanda Prevista": previsoes})

def treinar_multiplos_modelos(df, dias_futuros):
    resultados = []
    df['data'] = pd.to_datetime(df['data'])

    for produto in df['produto'].unique():
        df_prod = df[df['produto'] == produto].copy()

        if df_prod.empty:
            continue

        df_prod = preprocessar_dados(df_prod)

        if len(df_prod) < 2:
            continue

        X = df_prod[['dias']]
        y = df_prod['quantidade']

        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X, y)
        r2 = modelo.score(X, y)

        primeiro_dia = pd.to_datetime(df_prod['data'].min())
        ultimo_dia = df_prod['dias'].max()

        for i in range(1, dias_futuros + 1):
            dia_futuro = ultimo_dia + i
            data_prevista = primeiro_dia + timedelta(days=int(dia_futuro))
            pred = modelo.predict([[dia_futuro]])[0]
            demanda_prevista = max(0, round(pred, 2))

            resultados.append({
                "Produto": produto,
                "Data Prevista": data_prevista.date(),
                "Demanda Prevista": demanda_prevista,
                "Score R2": round(r2, 3)
            })

    if not resultados:
        raise ValueError("Nenhum produto possui dados suficientes para previsão.")

    return pd.DataFrame(resultados)