import time
import serial
import serial.tools.list_ports
import requests
import signal
import sys
import os
import hashlib
import json
from flask import Flask, request, jsonify
from signalrcore.hub_connection_builder import HubConnectionBuilder
from threading import Thread, Event


"""_summary_
Sequência de inicialização das conexões e dos métodos de encerramento seguro das conexões
"""
app = Flask(__name__)
stop_event = Event()

# Função para lidar com o sinal de interrupção (Ctrl+C)
def signal_handler(sig, frame):
    print("Encerrando a aplicação...") 
    stop_event.set
    if 'ser' in globals() and ser is not None and ser.is_open: 
        ser.close()
    flask_thread.join()
    sys.exit(0)

# Registrar o sinal de interrupção
signal.signal(signal.SIGINT, signal_handler)

def start_flask():
    app.run(host='localhost', port=5002, debug=True, use_reloader=False)

def close_existing_connections():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device == 'COM4':
            try:
                existing_serial = serial.Serial(port.device)
                existing_serial.close()
                print(f"Porta {port.device} fechada com sucesso.")
            except Exception as e:
                print(f"Erro ao fechar a porta {port.device}: {e}")

API_2_URL = 'http://localhost:5001/'
modelo = {1:["Crédito", True, False], 2:["Débito", False, True], 3:["Déb/Créd", True, True]}
start_pgto_erp = True
encerrar = False


# Configure as opções de SSL para ignorar a verificação de certificado
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

hub_connection = HubConnectionBuilder().with_url("https://localhost:7246/signalrhub", options={ 
    "verify_ssl": False # Ignorar a verificação de certificado
}).build()
# Funções de evento e início da conexão
hub_connection.on_open(lambda: print("Conexão estabelecida com sucesso")) 
hub_connection.on_close(lambda: print("Conexão fechada")) 
hub_connection.on_error(lambda data: print(f"Erro: {data}"))

hub_connection.start()

def main():
    close_existing_connections()
    for i in range(10):
        print(f'Tentativa {i+1} de conexão serial: PORT=COM4, BAUD(9600)')
        try:
            global ser 
            ser = serial.Serial('COM4', 9600)
            print("Porta COM4 aberta com sucesso") 
            break 
        except serial.SerialException as e:
            print(f"Erro ao abrir a porta COM4: {e}") 
            if 'ser' in locals() and ser.is_open:
                ser.close() 
        time.sleep(3) 
    if ser.is_open: 
        print("Serial está disponível e aberta.")
        global flask_thread
        flask_thread = Thread(target=start_flask)
        flask_thread.start()
        # Manter a thread principal ativa para capturar Ctrl+C 
        try: 
            while True: 
                time.sleep(1) 
        except KeyboardInterrupt:
            signal_handler(None, None)
    else: 
        print("Não foi possível abrir a porta serial após várias tentativas.")



#                   Classes

class DadosCadastro():
    def __init__(self, hx_cartao):
        self.cd_cartao = hash_cartao(hx_cartao)
        self.hx_cartao = hx_cartao
        self.ds_titular = None
        self.cpf_titular = None
        self.cd_password = None
        self.ds_operadora = None
        self.tp_credito = None
        self.tp_debito = None
    def ciclo_cadastro(self):
        self.entrada_titular()
        self.entrada_operadora()
        self.entrada_tp_cartao()
        return self.check_cadastro()
    def entrada_titular(self):
        while True:
            titular = input("Informe o titular: ")
            if str.isalpha(titular.replace(" ", "")):
                os.system('cls')
                self.ds_titular = titular.upper()
                break
            else:
                os.system('cls')
                print("NOME INVÁLIDO\n")
        while True:
            cpf = input("Informe cpf do titular(Apenas números): ")
            if str.isdigit(cpf) and len(cpf) == 11:
                os.system('cls')
                self.cpf_titular = cpf
                return
            else:
                os.system('cls')
                if not str.isdigit(cpf) and not len(cpf) == 11:
                    print("CPF com tamanho e caracteres inválidos\n")
                elif not str.isdigit(cpf):
                    print("CPF com caracteres inválidos\n")
                elif not len(cpf) == 11:
                    print("CPF com tamanho\n")
    def entrada_operadora(self):
        while True:
            operadora = input("Fornecedor do cartão: ")
            if str.isalpha(operadora.replace(" ","")):
                os.system('cls')
                self.ds_operadora = operadora.upper()
                return
            else:
                os.system('cls')
                print("NOME INVÁLIDO\n")
    def entrada_tp_cartao(self):
        while True:
            tp_cartao = input("Selecione o tipo:\n1-Crédito\n2-Débito\n3-Crédito e Débito\n=>")
            try:
                tp = int(tp_cartao)
                print(f'{tp} - {type(tp)}')
                print(modelo[tp])
                if tp in modelo.keys():
                    self.tp_credito = modelo[tp][1]
                    self.tp_debito = modelo[tp][2]
                return
            except:
                print("OPÇÃO INVÁLIDA\n")
    def check_cadastro(self):
        os.system('cls')
        while True:
            confirma = input(f'Confirme os dados:\nTitular:\t{self.ds_titular}\nNº Cartão:\t{self.cd_cartao}\nOperadora:\t{self.ds_operadora}\nCrédito:\t{"Sim" if self.tp_credito else "Não"}\nDébito:\t\t{"Sim" if self.tp_debito else "Não"}\n S-SIM \ N-NÃO >>')
            if confirma.upper() == 'S':
                while True:
                    pass_a = input("Digite uma senha para o cartao de 4 a 6 numeros >>")
                    if str.isdigit(pass_a) and 4<= len(pass_a) <=6:
                        break
                    else:
                        os.system('cls')
                        print('Senha inválida')
                pass_b = input("Confirme sua senha para o cartao >>")
                if pass_a == pass_b:
                    self.cd_password = pass_b
                    return True
                else:
                    os.system('cls')
                    print('Senhas divergentes \n\n')
            elif confirma.upper() == 'N':
                return False
            else:
                print('opção inválida')

class DadosPagamento():
    def __init__(self):
        self.vlr_total = None
        self.cd_cartao = None
        self.tp_trans = None
        self.ds_transacao = None
        self.tp_credito = None
        self.tp_debito = None
        self.parc_pgto = None
        self.cd_password = None
    def inicio_pgto_erp(self, dados):
        try:
            self.vlr_total = dados['Valor']
            self.tp_credito = True if dados['tp_pgto'] == 'Crédito' else False
            self.tp_debito = True if dados['tp_pgto'] == 'Débito' else False
            self.ds_transacao = dados['Empresa']
            self.parc_pgto = dados['Parcelas'] if 'Parcelas' in dados else None
            return "Dados recebidos, solicitando cartão", True
        except:
            return "Erro ao atribuir valores", False

    def cartao_pgto_check(self, dados):
        if type(dados) is not dict:
            return dados, False
        try:
            self.cd_cartao = hash_cartao(id_rfid_hex=dados['hx_cartao'])
            resposta = enviar_para_api_2(rota='verificar_cartao', cd_cartao=self.cd_cartao)
            if not resposta['Sucesso']:
                return resposta['msg'] if 'msg' in resposta else resposta['dados']['msg'], False
            dados = resposta['dados']
            if ((self.tp_credito and dados['tp_credito']) or (self.tp_debito and dados['tp_debito'])):
                return "Cartão validado", True
            return "Modo de pagamento inválido", False
        except:
            return "Erro na leitura do cartão", False    
        
    def senha_pgto_check(self, dados):
        if type(dados) is not dict:
            return dados, False
        try:
            self.cd_password = dados['pass']
            resposta = enviar_para_api_2(rota='valida_senha', 
                                         cd_cartao=self.cd_cartao, 
                                         cd_password=self.cd_password)
            if not resposta['Sucesso']:
                return resposta['msg'] if 'msg' in resposta else resposta['dados']['msg'], False
            return "Pagamento aprovado", True
        except:
            return "Erro na leitura da senha", False

    def ciclo_pgto_maq(self):

        self.entrada_modo_pagamento()
        self.entrada_valor()
        if self.check_pagamento():
            self.check_senha()
        else:
            envia_serial("CANCELADO")
    def entrada_modo_pagamento(self):
        while True:
            tp_cartao = input("Selecione o tipo de pagamento:\n1-Crédito\n2-Débito")
            try:
                if int(tp_cartao) in modelo.keys() and int(tp_cartao) != 3:
                    self.tp_credito = modelo[int(tp_cartao)][1]
                    self.tp_debito = modelo[int(tp_cartao)][2]
                break
            except:
                print("OPÇÃO INVÁLIDA\n")
    def entrada_valor(self):
        while True:
            try:
                self.valor = float(input("Valor da compra (use '.' para casa decimal): "))
                break
            except:
                os.system('cls')
                print("VALOR DIGITADO INVÁLIDO")
        os.system('cls')
        while True:
            try:
                self.parc_pgto = float(input("informe as parcelas (até 12x): "))
                break
            except:
                os.system('cls')
                print("VALOR DIGITADO INVÁLIDO")
    def check_pagamento(self):
        while True:
            os.system('cls')
            confirma = input(f'Confirme os dados:\nPagamento: {"Crédito" if (self.tp_credito and not self.tp_debito) else "Débito"}\nValor: {self.valor}\nParcelas: {self.parc_pgto}\nS-SIM \ N-NÃO >>')
            if confirma.upper() == 'S':
                print("Aguardando cartão...")
                envia_serial('EXIBIR_VALOR', valor=self.valor)
                self.cd_cartao = hash_cartao(ler_serial(origem='cad_cartao'))

                if enviar_para_api_2(rota='valida_pgto', dados={'cd_cartao':self.cd_cartao,
                                                                     'tp_pgto':'TP_CREDITO' if self.tp_credito  else 'TP_DEBITO'}): # rever na api2
                    return True
                else:
                    return False
            elif confirma.upper() == 'N':
                print('cadastro cancelado')
                envia_serial("CANCELADO")
                return False
            else:
                print('opção inválida')
    def check_senha(self):
        self.senha = envia_serial(comando='SOLICITA_SENHA',valor=self.valor).split('@')[2]
        enviar_para_api_2(rota='verificar_senha', dados={'cd_cartao':self.cd_cartao,
                                                         'senha':self.senha})
    def pagamento_maquininha(self,dados_maq):
        self.vlr_total = dados_maq.get("valor")
        self.cd_cartao = hash_cartao(dados_maq.get("hx_cartao"))
        self.tp_trans = 'Teste'
        self.ds_transacao = 'Teste'
        self.tp_credito = modelo[int(dados_maq.get("tp_pagamento"))][1]
        self.tp_debito = modelo[int(dados_maq.get("tp_pagamento"))][2]
        self.parc_pgto = dados_maq.get("parcelas") if modelo[int(dados_maq.get("tp_pagamento"))][1] else 0
        self.cd_password = dados_maq["pass"]


#           Métodos de processamento
def hash_cartao(id_rfid_hex):
    """_summary_

    Args:
        id_rfid_hex (_type_): _description_

    Returns:
        _type_: _description_
    """
    id_decimal = int(id_rfid_hex, 16)                                   # Converte de hex para decimal
    hash_val = hashlib.sha256(str(id_decimal).encode()).hexdigest()     # Aplica um hash para gerar o numero docartao
    complemento = int(hash_val[:6], 16)                                 # Armazena apenas 6 primeiros digitos
    num_cartao = str(id_decimal) + str(complemento)                     # Unifica o convertido com o hash
    if num_cartao[0] == '0':
        num_cartao = num_cartao[::-1]
    return num_cartao[:16]

def cadastra_cartao():
    """_summary_
    """
    print("Aguardando cartão...")
    envia_serial("\nCADASTRAR_CARTAO")
    cartao = ler_serial(origem='cad_cartao')
    NovoCadastro = DadosCadastro(cartao)
    os.system('cls')
    if NovoCadastro.ciclo_cadastro():
        enviar_para_api_2(rota='cadastra_cc',dados=NovoCadastro.__dict__)
        envia_serial("SUCESSO")
    else:
        print('cadastro cancelado')
        envia_serial("CANCELADO")
    
def ciclo_maquininha(data_dict, etapa):
    if etapa == 1:
        data_api = {"cd_cartao":hash_cartao(data_dict.get('hx_cartao')),
                    'tp_credito':modelo[data_dict.get('tp_pagamento')][1],
                    'tp_debito':modelo[data_dict.get('tp_pagamento')][2]}
        if enviar_para_api_2(rota='valida_pgto', dados_pgto=data_api):
            envia_serial('SUCESSO')
            return True
        else:
            envia_serial('erro')
            return False
    elif etapa == 2:
        data_api = {"cd_cartao":hash_cartao(data_dict.get('hx_cartao')),
                    'cd_password':data_dict.get('pass')}
        if enviar_para_api_2(rota='valida_senha', dados_pgto=data_api):
            envia_serial('SUCESSO')
            etapa = 3
        else:
            envia_serial('erro')
            return False
    if etapa == 3:
        NovoPagamento = DadosPagamento()
        print(data_dict)
        NovoPagamento.pagamento_maquininha(data_dict)
        if enviar_para_api_2(rota='insere_pgto', dados_pgto=NovoPagamento.__dict__):
            envia_serial('SUCESSO')
            etapa = 3
        else:
            envia_serial('erro')
            return False

def enviar_para_api_2(rota, **dados):
    """_summary_
    Function que realiza as requests para a api_financeira.py.

    Args:
        rota (str): _description_

    Returns:
        _type_: _description_
    """
    rota = API_2_URL + rota
    try:
        response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
        # Verifica o status da resposta
        if response.status_code == 200:
            return {'Sucesso':True, 'code':response.status_code, 'dados':response.json()}
        return {'Sucesso':False, 'code':response.status_code, 'dados':response.json()}
    except requests.exceptions.RequestException as e:
        return {'Sucesso':False, 
                'code':getattr(e.response, 'status_code', 'Sem código de status'), 
                'msg':str(e)}
   
#Método para processar variáveis JSON
def processar_json(json_string):
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return f"Erro ao decodificar: {json_string}"

# Métodos de interação com a serial port
def envia_serial(comando, valor=0):
    if comando in ['CARTAO_','SOLICITA_SENHA']:
        comando = comando + str(valor)
    ser.write(comando.encode())  # Envia o comando para o Arduino
    if comando in ['SUCESSO', 'ERRO']:
        return

def ler_serial():
    print('Lendo Serial......')
    while True:
        if ser.in_waiting > 0:
            dados = ser.readline().decode('utf-8').strip()
            return processar_json(dados)
            

#Métodos de interação com o ERP
@app.route('/start_sys', methods=['POST'])
def start_sys():
    dados = ler_serial()
    if "SYS" in dados and dados["SYS"] == "WAITING":
        envia_serial(comando="START_ERP")
    dados = ler_serial()
    print(dados)
    if "SYS" in dados:
        if dados['SYS'] in ["ON_ERP", "ON_LOCAL"]:
            return jsonify({'resp': 'Maquininha conectada com sucesso'}), 200
        elif dados['SYS'] == "ERROR":
            return jsonify({'resp': 'Requisição serial inapropriada ou com erro'}), 404
    return  jsonify({'resp': 'Requisição não gerou resposta apropriada'}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'resp': 'Comunicação com API [operacional]'}), 200

#Método que usa a maquininha para realizar o procedimento físico mas com dados de faturamento pelo ERP
@app.route('/fatura_maq', methods=['POST'])
def fatura_maq():
    #Transforma json em dicionário
    try:
        dados = request.get_json()
    except:
        return jsonify({"resp":"Dados corrompidos"})
    
    PagamentoMaquininha = DadosPagamento()
    msg, status = PagamentoMaquininha.inicio_pgto_erp(dados=dados)
    if not status:
        return jsonify({"resp":msg}), 400
    
    hub_connection.send("SendMessage", [msg]) # TODO Verificar porque não atualiza 
    
    envia_serial(comando="CARTAO_", valor=dados['Valor'])

    cartao = ler_serial()
    print(cartao)
    msg, status = PagamentoMaquininha.cartao_pgto_check(cartao)
    print(status)
    if not status:
        return jsonify({"resp":msg}), 203
    hub_connection.send("SendMessage", [msg])
    envia_serial(comando="SOLICITA_SENHA")
    msg, status = PagamentoMaquininha.senha_pgto_check(ler_serial())
    if not status:
        return jsonify({"resp":msg}), 203
    
    resposta = enviar_para_api_2(rota='/insere_pgto', **PagamentoMaquininha.__dict__)
    if not resposta['Sucesso']:
        return jsonify({'resp':resposta['msg'] if 'msg'in resposta else resposta['dados']}), 203
    return jsonify({"resp":msg}), 200




if __name__ == "__main__":
    main()