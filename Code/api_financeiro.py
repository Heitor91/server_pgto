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

@app.route('/verificar_cartao', methods=['POST'])
def verificar_cartao():
    """_summary_
    Endpoint para verificar se um cartão está registrado na base de dados.

    Este endpoint recebe uma requisição POST com um JSON contendo o número do cartão
    ('cd_cartao') e verifica se o cartão existe no banco de dados. Se o cartão for encontrado,
    retorna uma resposta com os tipos de pagamento associados (crédito e débito). Caso contrário,
    retorna uma mensagem indicando que o cartão não foi encontrado ou está inativo.

    Request Body:
        - cd_cartao (str): O número do cartão a ser verificado.
    Responses:
        - 200 OK: Se o cartão for encontrado, retorna uma mensagem de sucesso e os tipos de pagamento.
            Exemplo de resposta: {
                "msg": "Cartão encontrado",
                "tp_credito": <booleano para habilitado como crédito>,
                "tp_debito": <booleano para habilitado como débito>
            }
        - 400 Bad Request: Se o número do cartão não for fornecido no corpo da requisição.
            Exemplo de resposta: {
                "msg": "Numero do cartão não foi enviado"
            }
        - 404 Not Found: Se o cartão não for encontrado ou estiver inativo.
            Exemplo de resposta: {
                "msg": "Cartão não encontrado ou inativo"
            }
    """
    dados = request.get_json()
    if 'cd_cartao' not in dados or dados['cd_cartao'] is None:
        return jsonify({'msg': 'Numero do cartão não foi enviado'}), 400

    # Busca no Banco de dados se o cartão existe
    cartao = BaseCartoes.query.filter_by(cd_cartao=dados['cd_cartao']).first()

    #Retorna resultado da busca
    if cartao:
        return jsonify({'msg':'Cartão encontrado',
                        'tp_credito':cartao.tp_credito,
                        'tp_debito':cartao.tp_debito}),200
    else:
        return jsonify({'msg': 'Cartão não encontrado ou inativo'}), 404

@app.route('/valida_senha', methods=['POST'])
def valida_senha():
    dados = request.get_json()
    if 'cd_cartao' not in dados or 'cd_password' not in dados:
        return jsonify({'msg': 'Dados recebidos estão incompletos'}), 400
    
    # Busca no Banco de dados dados do cartão
    cartao = BaseCartoes.query.filter_by(cd_cartao=dados['cd_cartao']).first()
    if (dados['cd_password'] == cartao.cd_password):

        return jsonify({'msg':'Pagamento aprovado'}), 200
    else:
        return jsonify({'msg': 'Dados não correspondetes com a base'}), 400

@app.route('/insere_pgto', methods=['POST'])
def insere_pgto():
    dados = request.get_json()
    dados_trans = dados
    dados_cartao = BaseCartoes.query.filter_by(cd_cartao=dados['cd_cartao']).first().__dict__

    campos={'campos_conta':['cd_cartao','doc_transacao','cpf_titular','tp_trans','ds_transacao','credito','debito','saldo'],
    'campos_cred':['cd_cartao','ds_transacao','parc_pgto','cpf_titular','vlr_total']}

    tp_pgto = None
    if dados_trans['tp_credito']:
        tp_pgto = 'campos_cred'
    else:
        dados['debito'] = dados['vlr_total']
        dados['doc_transacao'] = randrange(1,9999999)
        dados['credito'] = 0
        dados['saldo'] = 0
        tp_pgto = 'campos_conta'
    dados_pgto = {}
    for campo in campos[tp_pgto]:
        if campo == 'tp_trans':
            dados_pgto[campo] = 'DEBITO DEBTS**PAG'
        elif campo in dados_trans.keys():
            dados_pgto[campo] = dados_trans.get(campo)
        elif campo in dados_cartao.keys():
            dados_pgto[campo] = dados_cartao.get(campo)
    if dados_trans['tp_credito']:
        novo_cartao = CartaoCredito(**dados_pgto)
    elif dados_trans['tp_debito']:
        novo_cartao = ContaCorrente(**dados_pgto)
    db.session.add(novo_cartao)
    db.session.commit()
    return jsonify({'mensagem': 'Pagamento registrado com sucesso'}), 200

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


@app.route('/open_finance_request', methods=['POST'])
def open_finance_request():
    pass

@app.route('/open_finance_refresh', methods=['POST'])
def open_finance_refresh():
    pass

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5001)
