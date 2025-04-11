from datetime import datetime
from database import session, Venda

def inserir_venda(data_str, quantidade, produto=None, valor=None):
    if quantidade < 1 or valor is None or valor < 0.01:
        print("Quantidade deve ser maior que 0 e valor deve ser maior que 0.")
        return
    data = datetime.strptime(data_str, '%Y-%m-%d').date()
    venda = Venda(data=data, quantidade=quantidade, produto=produto, valor=valor)
    session.add(venda)
    session.commit()
    print(f'Venda inserida: {venda}')

if __name__ == "__main__":
    inserir_venda('2023-04-01', 10, 'Produto A', 150.0)
    inserir_venda('2023-04-02', 15, 'Produto B', 250.0)
    inserir_venda('2023-04-03', 5, 'Produto C', 110.0)