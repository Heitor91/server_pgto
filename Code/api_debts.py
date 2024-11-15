from datetime import date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import BigInteger
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Double, Date, SmallInteger
import requests

app = Flask(__name__)

# Configurando o banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:heitor13@localhost/debts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Ref_Empresas(db.Model):
    __tablename__ = "REF_EMPRESAS"

    cnpj = Column('CNPJ', BigInteger, primary_key=True)
    nome_empresa = Column('NOME_EMPRESA', String(200), nullable=False)
    ramo_empresa = Column('RAMO_EMPRESA', Integer, ForeignKey('REF_RAMOS.ID_RAMO'), nullable=False)
    recorrencia = Column('RECORRENCIA', SmallInteger, default=0)

class Ref_Ramos(db.Model):
    __tablename__ = "REF_RAMOS"

    id_ramo = Column('ID_RAMO', Integer, primary_key=True)
    nome_ramo = Column('NOME_RAMO', String(40), nullable=False)
    essencial = Column('ESSENCIAL', SmallInteger, default=0)

class Usuario(db.Model):
    __tablename__ = 'USUARIO'
    
    id_usuario = Column('ID_USUARIO', BigInteger, primary_key=True, autoincrement=True)
    nome = Column('NOME_USUARIO', String(200), nullable=False)
    login = Column('EMAIL_USUARIO', String(50), nullable=False)
    senha = Column('SENHA_USUARIO', String(10), nullable=False)
    cpf = Column('CPF_USUARIO', String(11), nullable=False)

class Questionario(db.Model):
    __tablename__ = 'QUESTIONARIO'
    
    id_questionario = Column('ID_QUESTIONARIO', Integer, primary_key=True, autoincrement=True)
    id_usuario = Column('ID_USUARIO', BigInteger, ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    dt_questionario = Column('DT_QUESTIONARIO', Date, nullable=False, default=date.today)
    tp_investimentos = Column('TP_INVESTIMENTOS', JSON, nullable=False)
    tx_uso_ecommerce = Column('TX_USO_ECOMMERCE', Integer, nullable=False)
    tx_uso_transporte = Column('TX_USO_TRANSPORTE', Integer, nullable=False)
    tx_uso_app_entrega = Column('TX_USO_APP_ENTREGA', Integer, nullable=False)

class Entradas_NRastreadas(db.Model):
    __tablename__ = 'ENTRADAS_NRASTRADAS'
    
    id_entrada = Column('ID_ENTRADA', BigInteger, primary_key=True, autoincrement=True)
    usuario = Column('USUARIO', BigInteger, ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    ds_entrada = Column('DS_ENTRADA', String(200), default=0)
    recorrencia = Column('RECORRENCIA', SmallInteger, default=0)
    valor = Column('VALOR', Date, nullable=False, default=date.today)
    dt_recorrencia = Column('DT_RECORRENCIA', Date, nullable=False)
    dt_entrada = Column('DT_ENTRADA', Date, nullable=False)

class Cartao(db.Model):
    __tablename__ = 'CARTOES'
    
    cd_cartao = Column('CD_CARTAO', BigInteger, primary_key=True)
    usuario = Column('USUARIO', BigInteger, ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    ds_operadora = Column('DS_OPERADORA', String(45), nullable=False)
    tp_credito = Column('TP_CREDITO', SmallInteger, default=0)
    tp_debito = Column('TP_DEBITO', SmallInteger, default=0)
    saldo = Column('SALDO', Float, default=0)
    limite = Column('LIMITE', Float, default=0)
    dt_fatura = Column('FECHAMENTO_FAT', DateTime)

class Trans_Conta(db.Model):
    __tablename__ = 'TRANS_CONTA'
    
    id_trans = Column('ID_TRANS', BigInteger, primary_key=True, autoincrement=True)
    cd_cartao = Column('CD_CARTAO', BigInteger, ForeignKey('CARTOES.CD_CARTAO'), nullable=False)
    dt_trasacao = Column('DT_TRANSACAO', Date, nullable=False)
    cnpj_transacao =  Column('CNPJ_TRANSACAO', BigInteger, ForeignKey('REF_EMPRESAS.CNPJ'), nullable=False)
    vlr_credito = Column('VLR_CREDITO', Float)
    vlr_debito = Column('VLR_DEBITO', Float)

class Trans_Credito(db.Model):
    __tablename__ = 'TRANS_CREDITO'
    
    id_trans = Column('ID_TRANS', Integer, primary_key=True, autoincrement=True)
    cd_cartao = Column('CD_CARTAO', BigInteger, ForeignKey('CARTOES.CD_CARTAO'), nullable=False)
    dt_trasacao = Column('DT_TRANSACAO', Date, nullable=False)
    cnpj_transacao =  Column('CNPJ_TRANSACAO', BigInteger, ForeignKey('REF_EMPRESAS.CNPJ'), nullable=False)
    parc_pgto = Column('PARC_PGTO', Integer)
    vlr_total = Column('VLR_TOTAL', Float)

class Metas(db.Model):
    __tablename__ = 'METAS'

    id_meta = Column('ID_TRANS', BigInteger, primary_key=True, autoincrement=True)
    usuario = Column('USUARIO', BigInteger, ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    cartao = Column('CARTAO', BigInteger, ForeignKey('CARTOES.CD_CARTAO'))
    vlr_inicial = Column('VLR_INICIAL', Float, nullable=False)
    perc_meta = Column('PERC_META', Float, nullable=False)
    dt_meta_inicio = Column('DT_META_INICIO', Date, nullable=False)
    dt_meta_conclusao = Column('DT_META_CONCLUSAO', Date, nullable=False)
    ramo_meta = Column('RAMO_META', Integer, ForeignKey('REF_RAMOS.ID_RAMO'))

# Criação das tabelas
with app.app_context():
    db.create_all()

@app.route('/notifica_pgto', methods=['POST'])
def notifica_pgto():
    pass

@app.route('/open_finance', methods=['POST'])
def open_finance():
    pass

if __name__ == '__main__':
    app.run(port=5002)
