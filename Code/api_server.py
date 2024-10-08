from datetime import date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Double, Date, SmallInteger
import requests
from random import randrange

app = Flask(__name__)

# Configurando o banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:heitor13@localhost/debts'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ContaCorrente(db.Model):
    __tablename__ = 'BNC_CONTACORRENTE'
    
    id_trans = Column('ID_TRANS', BigInteger, primary_key=True)
    cd_cartao = Column('CD_CARTAO', BigInteger, ForeignKey('BNC_CONTROLE_CARTOES.CD_CARTAO'), nullable=False)
    doc_transacao = Column('DOC_TRANSACAO', Double, nullable=False)
    cpf_titular = Column('CPF_CLIENTE', String(45), nullable=False)
    dt_transacao = Column('DT_PGTO', Date, nullable=False, default=date.today)
    tp_trans = Column('TP_TRANS', String(100), nullable=False)
    ds_transacao = Column('DS_TRANSACAO', String(100), nullable=False)
    credito = Column('CREDITO', Float)
    debito = Column('DEBITO', Float)
    saldo = Column('SALDO', String(45), nullable=False)

class CartaoCredito(db.Model):
    __tablename__ = 'BNC_CARTAOCREDITO'
    
    id_trans = Column('ID_TRANS', BigInteger, primary_key=True)
    cd_cartao = Column('CD_CARTAO', BigInteger, ForeignKey('BNC_CONTROLE_CARTOES.CD_CARTAO'), nullable=False)
    dt_transacao = Column('DT_TRANSACAO', Date, nullable=False, default=date.today)
    ds_transacao = Column('DS_TRANSACAO', String(100), nullable=False)
    parc_pgto = Column('PARC_PGTO', Integer, nullable=False)
    cpf_titular = Column('CPF_CLIENTE', String(11), nullable=False)
    vlr_total = Column('VLR_TOTAL', Float, nullable=False)

class BaseCartoes(db.Model):
    __tablename__ = 'BNC_CONTROLE_CARTOES'

    cd_cartao = Column('CD_CARTAO', BigInteger, primary_key=True)
    hx_cartao = Column('HX_CARTAO', String(8), nullable=False)
    ds_titular = Column('DS_TITULAR', String(100), nullable=False)
    cpf_titular = Column('CPF_TITULAR', String(11), nullable=False)
    cd_password = Column('CD_PASS', String(11), nullable=False)
    ds_operadora = Column('DS_OPERADORA', String(11), nullable=False)
    tp_credito = Column('TP_CREDITO', SmallInteger, nullable=False)
    tp_debito = Column('TP_DEBITO', SmallInteger, nullable=False)


# Criação das tabelas
with app.app_context():
    db.create_all()

#====================================================================================================================
#  Endpoint para cadastrar cartao
@app.route('/cadastra_cc', methods=['POST'])
def cadastra_cartao():
    print('CADASTRO SOLICITADO')
    dados = request.get_json()['dados']
    print(dados)
    if not dados:
        print('Nenhum dado recebido ou dados')
        return jsonify({'erro': 'Nenhum dado recebido'}), 400

    if len(dados) != 8:
        print('Dados incompletos')
        return jsonify({'erro': 'Dados incompletos'}), 400
    
    validador = requests.post('http://localhost:5001/verificar_cartao',json={'cd_cartao': dados['cd_cartao']})
    if validador.json().get('valido'):
        print('Cartão já registrado, operação cancelada')
        return jsonify({'mensagem': 'Cartão já registrado, operação cancelada'}), 220
    else:
        novo_cartao = BaseCartoes(**dados)
        db.session.add(novo_cartao)
        db.session.commit()
        print('Cartão registrado com sucesso')
        return jsonify({'mensagem': 'Cartão registrado com sucesso'}), 201

# Endpoint para verificar se o cartão é vjá está na base ou não
@app.route('/verificar_cartao', methods=['POST'])
def verificar_cartao():
    dados = request.get_json()
    if 'dados' in dados:
        dados = dados['dados']
    print(dados)
    if 'cd_cartao' not in dados:
        return jsonify({'erro': 'Numero do cartão não foi enviado'}), 400

    # Verificar se o cartão está registrado e ativo
    cartao = BaseCartoes.query.filter_by(cd_cartao=dados['cd_cartao']).first()

    if cartao:
        print('Cartão válido')
        return jsonify({'valido': True, 'mensagem': 'Cartão válido'})
    else:
        print('Cartão não encontrado ou inativo')
        return jsonify({'valido': False, 'mensagem': 'Cartão não encontrado ou inativo'}), 404

@app.route('/valida_senha', methods=['POST'])
def valida_senha():
    dados = request.get_json()
    if 'cd_cartao' not in dados["dados_pgto"] and 'cd_password' not in dados['dados_pgto']:
        return jsonify({'erro': 'ID do cartão não foi enviado'}), 400
    cartao = BaseCartoes.query.filter_by(cd_cartao=dados['dados_pgto']['cd_cartao']).first()
    print(dados['dados_pgto']['cd_password'])
    print(cartao.cd_password)
    if (dados['dados_pgto']['cd_password'] == cartao.cd_password):
        return jsonify({'valido': True, 'mensagem': 'Cartão válido'}), 201
    else:
        return jsonify({'erro': 'Método de pagamento inválido'}), 400

@app.route('/valida_pgto', methods=['POST'])
def valida_pgto():
    dados = request.get_json()
    campos = ['cd_cartao', 'tp_credito', 'tp_credito'] 
    if not all(chave in dados['dados_pgto'] for chave in campos):
        return jsonify({'erro': 'Campo faltante'}), 400 
    
    cartao = BaseCartoes.query.filter_by(cd_cartao=dados['dados_pgto']['cd_cartao']).first()
    
    if (dados['dados_pgto']['tp_credito'] and cartao.tp_credito) or (dados['dados_pgto']['tp_debito'] and cartao.tp_debito):
        return jsonify({'valido': True, 'mensagem': 'Cartão válido'}), 201
    else:
        return jsonify({'erro': 'Método de pagamento inválido'}), 400

@app.route('/insere_pgto', methods=['POST'])
def insere_pgto():
    dados = request.get_json()
    dados_trans = dados['dados_pgto']
    dados_cartao = BaseCartoes.query.filter_by(cd_cartao=dados['dados_pgto']['cd_cartao']).first().__dict__
    campos={'campos_conta':['cd_cartao','doc_transacao','cpf_titular','tp_trans','ds_transacao','credito','debito','saldo'],
    'campos_cred':['cd_cartao','ds_transacao','parc_pgto','cpf_titular','vlr_total']}
    tp_pgto = None
    if dados_trans['tp_credito']:
        tp_pgto = 'campos_cred'
    else:
        dados['dados_pgto']['debito'] = dados['dados_pgto']['vlr_total']
        dados['dados_pgto']['doc_transacao'] = randrange(1,9999999)
        dados['dados_pgto']['credito'] = 0
        dados['dados_pgto']['saldo'] = 0
        tp_pgto = 'campos_conta'
    dados_pgto = {}
    for campo in campos[tp_pgto]:
        print(campo)
        if campo in dados_trans.keys():
            dados_pgto[campo] = dados_trans.get(campo)
        elif campo in dados_cartao.keys():
            dados_pgto[campo] = dados_cartao.get(campo)
    if dados_trans['tp_credito']:
        novo_cartao = CartaoCredito(**dados_pgto)
    elif dados_trans['tp_debito']:
        novo_cartao = ContaCorrente(**dados_pgto)
    db.session.add(novo_cartao)
    db.session.commit()
    print('Cartão registrado com sucesso')
    return jsonify({'mensagem': 'Pagamento registrado com sucesso'}), 201

if __name__ == '__main__':
    app.run(port=5001)
