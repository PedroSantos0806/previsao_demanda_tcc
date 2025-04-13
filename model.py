import pandas as pd
from sklearn.linear_model import LinearRegression
from database import session, Venda

def carregar_dados(usuario_id):
    vendas = session.query(Venda).filter_by(usuario_id=usuario_id).all()
    dados = [{
        "data": venda.data,
        "quantidade": venda.quantidade,
        "valor": venda.valor
    } for venda in vendas]
    return pd.DataFrame(dados)

def treinar_modelo(df):
    """
    Treina o modelo de regressão linear com base na quantidade vendida por dia.
    Retorna o modelo treinado e o último dia como referência para previsão.
    """
    df = preparar_dados(df)
    X = df[['dias']]
    y = df['quantidade']
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    ultimo_dia = df['dias'].max()
    return modelo, ultimo_dia

def prever_demanda(modelo, ultimo_dia, dias=7):
    """
    Gera as previsões de demanda para os próximos `dias`.
    """
    dias_futuros = [[ultimo_dia + i + 1] for i in range(dias)]
    previsoes = modelo.predict(dias_futuros)
