
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.orm import relationship, backref



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

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha = Column(String(100), nullable=False)

    vendas = relationship('Venda', backref='usuario')

# Modelo da Tabela de Vendas
class Venda(Base):
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    quantidade = Column(Integer, nullable=False)
    produto = Column(String(100), nullable=False)
    valor = Column(Float, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabela 'vendas' criada com sucesso no banco Railway.")