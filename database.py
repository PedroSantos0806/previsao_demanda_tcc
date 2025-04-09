
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os


MYSQL_USER = 'root'
MYSQL_PASSWORD = 'cVUGBLbWwCeJcvbXtsKEUodzlThjcauU'
MYSQL_HOST = 'switchyard.proxy.rlwy.net'
MYSQL_PORT = '39084'
MYSQL_DB = 'railway'


DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"


engine = create_engine(DATABASE_URL)


Base = declarative_base()


Session = sessionmaker(bind=engine)
session = Session()


# Modelo da Tabela de Vendas
class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    quantidade = Column(Integer, nullable=False)
    produto = Column(String(100), nullable=True)
    valor = Column(Float, nullable=True)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabela 'vendas' criada com sucesso no banco Railway.")