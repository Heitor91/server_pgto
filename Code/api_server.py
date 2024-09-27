from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Double, Date, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import requests

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///debts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Configurando o banco de dados MySQL
engine = create_engine("mysql://root:heitor13@localhost/debts")
db = SQLAlchemy(app)

# Modelo de dados
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'DBTS_USUARIO'
    
    id_usuario = Column('ID_USUARIO', Integer, primary_key=True)
    nome = Column('NOME', String(200), nullable=False)
    login = Column('LOGIN', String(20), nullable=False)
    senha = Column('SENHA', String(20), nullable=False)
    cpf = Column('CPF', String(11), nullable=False)
    dt_cadastro = Column('DT_CADASTRO', DateTime, nullable=False)

class Questionario(Base):
    __tablename__ = 'DBTS_QUESTIONARIO'
    
    id_questionario = Column('ID_QUESTIONARIO', Integer, primary_key=True, autoincrement=True)
    id_usuario = Column('ID_USUARIO', Integer, ForeignKey('DBTS_USUARIO.ID_USUARIO'), nullable=False)
    dt_questionario = Column('DT_QUESTIONARIO', Date, nullable=False, server_default=func.current_date())
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

class Cartao(Base):
    __tablename__ = 'DBTS_CARTOES'
    
    num_cartao = Column('NUM_CARTAO', Double, primary_key=True)
    cpf = Column('CPF', String(11), nullable=False)
    banco = Column('BANCO', String(100), nullable=False)
    id_usuario = Column('ID_USUARIO', Integer, ForeignKey('DBTS_USUARIO.ID_USUARIO'), nullable=False)
    tp_cartao = Column('TP_CARTAO', String(45), nullable=False)
    fechamento_fat = Column('FECHAMENTO_FAT', DateTime)
    limite = Column('LIMITE', Float)

class Transacao(Base):
    __tablename__ = 'DBTS_TRANSACOES'
    
    id_transacao = Column('ID_TRANSACAO', Integer, primary_key=True, autoincrement=True)
    num_cartao = Column('NUM_CARTAO', Double, ForeignKey('DBTS_CARTOES.NUM_CARTAO'), nullable=False)
    tp_pgto = Column('TP_PGTO', String(100), nullable=False)
    ds_pgto = Column('DS_PGTO', String(100), nullable=False)
    dt_pgto = Column('DT_PGTO', Date, nullable=False)
    vlr_credito = Column('VLR_CREDITO', Float)
    vlr_debito = Column('VLR_DEBITO', Float)
    qtd_parcelas = Column('QTD_PARCELAS', Integer)

class ContaCorrente(Base):
    __tablename__ = 'BNC_CONTACORRENTE'
    
    id_trans = Column('ID_TRANS', Double, primary_key=True)
    cod_cartao = Column('COD_CARTAO', Double, ForeignKey('BNC_CONTROLE_CARTOES.COD_CARTAO'), nullable=False)
    doc_transacao = Column('DOC_TRANSACAO', Double, nullable=False)
    cpf_cliente = Column('CPF_CLIENTE', String(45), nullable=False)
    dt_transacao = Column('DT_PGTO', Date, nullable=False)
    tp_trans = Column('TP_TRANS', String(100), nullable=False)
    ds_transacao = Column('DS_TRANSACAO', String(100), nullable=False)
    credito = Column('CREDITO', Float)
    debito = Column('DEBITO', Float)
    saldo = Column('SALDO', String(45), nullable=False)

class CartaoCredito(Base):
    __tablename__ = 'BNC_CARTAOCREDITO'
    
    id_trans = Column('ID_TRANS', Double, primary_key=True)
    cod_cartao = Column('COD_CARTAO', Double, ForeignKey('BNC_CONTROLE_CARTOES.COD_CARTAO'), nullable=False)
    dt_transacao = Column('DT_TRANSACAO', Date, nullable=False)
    ds_transacao = Column('DS_TRANSACAO', String(100), nullable=False)
    parc_pgto = Column('PARC_PGTO', Integer, nullable=False)
    cpf_cliente = Column('CPF_CLIENTE', String(11), nullable=False)
    vlr_total = Column('VLR_TOTAL', Float, nullable=False)

class BaseCartoes(Base):
    __tablename__ = 'BNC_CONTROLE_CARTOES'

    cd_cartao = Column('ID_TRANS', Double, primary_key=True)
    hx_cartao = Column('COD_CARTAO', String(8), nullable=False)
    ds_titular = Column('DS_TRANSACAO', String(100), nullable=False)
    cpf_cliente = Column('CPF_CLIENTE', String(11), nullable=False)
    tp_credito = Column('PARC_PGTO', SmallInteger, nullable=False)
    tp_debito = Column('VLR_TOTAL', SmallInteger, nullable=False)


#Bases SQLite
"""class Cartao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartao_id = db.Column(db.String(80), nullable=False)
    nome_tit = db.Column(db.String(120), nullable=False)
    tp_cartao = db.Column(db.String(10), nullable=False)

    def __init__(self, cartao_id, nome_tit, tp_cartao):
        self.cartao_id = cartao_id
        self.nome_tit = nome_tit
        self.tp_cartao = tp_cartao

class Pagamentos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartao_id = db.Column(db.String(80), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tp_pgto = db.Column(db.String(10), nullable=False)
    def __init__(self, cartao_id, valor, tp_pgto):
        self.cartao_id = cartao_id
        self.valor = valor
        self.tp_pgto =tp_pgto"""

# Criação das tabelas
with app.app_context():
    db.create_all()

@app.route('/pagamento', methods=['POST'])
def pagamento():
    print('PROCESSANDO PAGAMENTO')
    dados = request.get_json()
    if not dados:
        print('Nenhum dado recebido')
        return jsonify({'erro': 'Nenhum dado recebido'}), 400
    
    cartao_id = dados.get('id_cartao')
    valor = dados.get('valor')
    operacao = dados.get('tp_cartao')

    print(f'Cartão: {cartao_id}/Valor: {valor}/ operação: {operacao}')

    if not cartao_id or not valor or not operacao:
        print('Dados incompletos')
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    validador = requests.post('http://localhost:5001/verificar_cartao',json={'id_cartao': cartao_id})
    if validador.json().get('valido'):
        novo_pgto = Pagamentos(cartao_id=cartao_id, valor=valor, tp_pgto=operacao)
        db.session.add(novo_pgto)
        db.session.commit()
        return jsonify({'mensagem': 'Pagamento registrado com sucesso'}), 201
    else:
        print('Cartão não registrado, operação cancelada')
        return jsonify({'mensagem': 'Cartão não registrado, operação cancelada'}), 221

# Rota para receber os dados via POST
@app.route('/cadastra_cc', methods=['POST'])
def cadastra_cartao():
    print('CADASTRO SOLICITADO')
    dados = request.get_json()
    if not dados:
        print('Nenhum dado recebido')
        return jsonify({'erro': 'Nenhum dado recebido'}), 400

    cartao_id = dados.get('id_cartao')
    titular = dados.get('nome_titular')
    operacao = dados.get('tp_cartao')

    if not cartao_id or not titular or not operacao:
        print('Dados incompletos')
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    validador = requests.post('http://localhost:5001/verificar_cartao',json={'id_cartao': cartao_id})
    if validador.json().get('valido'):
        print('Cartão já registrado, operação cancelada')
        return jsonify({'mensagem': 'Cartão já registrado, operação cancelada'}), 220
    else:
        novo_cartao = Cartao(cartao_id=cartao_id, nome_tit=titular, tp_cartao=operacao)
        db.session.add(novo_cartao)
        db.session.commit()
        print('Cartão registrado com sucesso')
        return jsonify({'mensagem': 'Cartão registrado com sucesso'}), 201

# Endpoint para verificar se o cartão é válido
@app.route('/verificar_cartao', methods=['POST'])
def verificar_cartao():
    dados = request.get_json()
    if 'id_cartao' not in dados:
        return jsonify({'erro': 'ID do cartão não foi enviado'}), 400

    id_cartao = dados['id_cartao']

    # Verificar se o cartão está registrado e ativo
    cartao = Cartao.query.filter_by(cartao_id=id_cartao).first()

    if cartao:
        print('Cartão válido')
        return jsonify({'valido': True, 'mensagem': 'Cartão válido'})
    else:
        print('Cartão não encontrado ou inativo')
        return jsonify({'valido': False, 'mensagem': 'Cartão não encontrado ou inativo'}), 404

if __name__ == '__main__':
    app.run(port=5001)
