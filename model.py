import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression


usuario = 'root'
senha = 'cVUGBLbWwCeJcvbXtsKEUodzlThjcauU'
host = 'switchyard.proxy.rlwy.net'
porta = '39084'
banco = 'railway'
database_url = f'mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}'

def carregar_dados():
    engine = create_engine(database_url)
    df = pd.read_sql('SELECT * FROM vendas', con=engine)
    return df

def preparar_dados(df):
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    df['dias'] = (df['data'] - df['data'].min()).dt.days
    return df

def treinar_modelo(df):
    df = preparar_dados(df)
    x = df[['dias']]
    y = df['quantidade']
    modelo = LinearRegression()
    modelo.fit(x, y)
    return modelo, df['dias'].max()

def prever_demanda(modelo, ultimo_dia, dias_previsao=7):
    novos_dias = pd.DataFrame({'dias': list(range(ultimo_dia+1, ultimo_dia+1+dias_previsao))})
    previsao = modelo.predict(novos_dias)
    novos_dias['previsao'] = previsao
    return novos_dias

if __name__ == "__main__":
    df = carregar_dados()
    if df.empty:
        print("Nenhum dado encontrado na tabela 'vendas'.")
    else:
        modelo, ultimo_dia = treinar_modelo(df)
        previsao = prever_demanda(modelo, ultimo_dia, 7)
        print("Previsão de vendas para os próximos dias:")
        print(previsao[['dias', 'previsao']])