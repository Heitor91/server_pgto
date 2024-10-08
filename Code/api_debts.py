from datetime import date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Double, Date, SmallInteger
import requests

app = Flask(__name__)

# Configurando o banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:heitor13@localhost/debts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'DBTS_USUARIO'
    
    id_usuario = Column('ID_USUARIO', Integer, primary_key=True)
    nome = Column('NOME', String(200), nullable=False)
    login = Column('LOGIN', String(20), nullable=False)
    senha = Column('SENHA', String(20), nullable=False)
    cpf = Column('CPF', String(11), nullable=False)
    dt_cadastro = Column('DT_CADASTRO', DateTime, nullable=False)

class Questionario(db.Model):
    __tablename__ = 'DBTS_QUESTIONARIO'
    
    id_questionario = Column('ID_QUESTIONARIO', Integer, primary_key=True, autoincrement=True)
    id_usuario = Column('ID_USUARIO', Integer, ForeignKey('DBTS_USUARIO.ID_USUARIO'), nullable=False)
    dt_questionario = Column('DT_QUESTIONARIO', Date, nullable=False, default=date.today)
    inv_poupanca = Column('INV_POUPANCA', SmallInteger, default=0)
    inv_tit_publico = Column('INV_TIT_PUBLICO', SmallInteger, default=0)
    inv_tit_captalizacao = Column('INV_TIT_CAPTALIZACAO', SmallInteger, default=0)
    inv_consorcio = Column('INV_CONSORCIO', SmallInteger, default=0)
    inv_fund_imobiliario = Column('INV_FUND_IMOBILIARIO', SmallInteger, default=0)
    inv_fund_multimercado = Column('INV_FUND_MULTIMERCADO', SmallInteger, default=0)
    inv_tesouro_diret = Column('INV_TESOURO_DIRET', SmallInteger, default=0)
    inv_acoes = Column('INV_ACOES', SmallInteger, default=0)
    ccred_ecommerce = Column('CCRED_ECOMMERCE', Integer, default=0)
    ccred_transporte = Column('CCRED_TRNSPORTE', Integer, default=0)
    ccred_delivery = Column('CCRED_DELIVERY', Integer, default=0)

class Cartao(db.Model):
    __tablename__ = 'DBTS_CARTOES'
    
    num_cartao = Column('NUM_CARTAO', BigInteger, primary_key=True)
    cpf = Column('CPF', String(11), nullable=False)
    banco = Column('BANCO', String(100), nullable=False)
    id_usuario = Column('ID_USUARIO', Integer, ForeignKey('DBTS_USUARIO.ID_USUARIO'), nullable=False)
    tp_cartao = Column('TP_CARTAO', String(45), nullable=False)
    fechamento_fat = Column('FECHAMENTO_FAT', DateTime)
    limite = Column('LIMITE', Float)

class Transacao(db.Model):
    __tablename__ = 'DBTS_TRANSACOES'
    
    id_transacao = Column('ID_TRANSACAO', Integer, primary_key=True, autoincrement=True)
    num_cartao = Column('NUM_CARTAO', BigInteger, ForeignKey('DBTS_CARTOES.NUM_CARTAO'), nullable=False)
    tp_pgto = Column('TP_PGTO', String(100), nullable=False)
    ds_pgto = Column('DS_PGTO', String(100), nullable=False)
    dt_pgto = Column('DT_PGTO', Date, nullable=False)
    vlr_credito = Column('VLR_CREDITO', Float)
    vlr_debito = Column('VLR_DEBITO', Float)
    qtd_parcelas = Column('QTD_PARCELAS', Integer)

@app.route('/notifica_pgto', method=['POST'])
def notifica_pgto():
    pass

@app.route('/open_finance', method=['POST'])
def open_finance():
    pass

if __name__ == '__main__':
    app.run(port=5001)
