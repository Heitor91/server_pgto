import serial
import requests
import os
import sys
import time
import msvcrt
import hashlib
import json

#====================================================================================================================
#                   Variáveis Globais
#====================================================================================================================
ser = serial.Serial('COM4', 9600)  # Use a porta correta
API_2_URL = 'http://localhost:5001/'
modelo = {1:["Crédito", True, False], 2:["Débito", False, True], 3:["Déb/Créd", True, True]}



#====================================================================================================================
#                   Classes
#====================================================================================================================
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
    def ciclo_pagamento(self):
        self.entrada_modo_pagamento()
        self.entrada_valor()
        if self.check_pagamento():
            self.check_senha()
        else:
            send_serial_cmd("CANCELADO")
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
                send_serial_cmd('EXIBIR_VALOR', valor=self.valor)
                self.cd_cartao = hash_cartao(monitorar_serial(origem='cad_cartao'))

                if enviar_para_api_2(rota='valida_pgto', dados={'cd_cartao':self.cd_cartao,
                                                                     'tp_pgto':'TP_CREDITO' if self.tp_credito  else 'TP_DEBITO'}): # rever na api2
                    return True
                else:
                    return False
            elif confirma.upper() == 'N':
                print('cadastro cancelado')
                send_serial_cmd("CANCELADO")
                return False
            else:
                print('opção inválida')
    def check_senha(self):
        self.senha = send_serial_cmd(comando='SOLICITA_SENHA',valor=self.valor).split('@')[2]
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


#====================================================================================================================
#                  Métodos
#====================================================================================================================

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
    send_serial_cmd("\nCADASTRAR_CARTAO")
    cartao = monitorar_serial(origem='cad_cartao')
    NovoCadastro = DadosCadastro(cartao)
    os.system('cls')
    if NovoCadastro.ciclo_cadastro():
        enviar_para_api_2(rota='cadastra_cc',dados=NovoCadastro.__dict__)
        send_serial_cmd("SUCESSO")
    else:
        print('cadastro cancelado')
        send_serial_cmd("CANCELADO")
    
def pagamento():
    os.system('cls')
    NovoPagamento = DadosPagamento()
    NovoPagamento.ciclo_pagamento()
    enviar_para_api_2(rota='pagamento',dados=NovoPagamento.__dict__)

def ciclo_maquininha(data_dict, etapa):
    if etapa == 1:
        data_api = {"cd_cartao":hash_cartao(data_dict.get('hx_cartao')),
                    'tp_credito':modelo[data_dict.get('tp_pagamento')][1],
                    'tp_debito':modelo[data_dict.get('tp_pagamento')][2]}
        if enviar_para_api_2(rota='valida_pgto', dados_pgto=data_api):
            send_serial_cmd('SUCESSO')
            return True
        else:
            send_serial_cmd('erro')
            return False
    elif etapa == 2:
        data_api = {"cd_cartao":hash_cartao(data_dict.get('hx_cartao')),
                    'cd_password':data_dict.get('pass')}
        if enviar_para_api_2(rota='valida_senha', dados_pgto=data_api):
            send_serial_cmd('SUCESSO')
            etapa = 3
        else:
            send_serial_cmd('erro')
            return False
    if etapa == 3:
        NovoPagamento = DadosPagamento()
        print(data_dict)
        NovoPagamento.pagamento_maquininha(data_dict)
        if enviar_para_api_2(rota='insere_pgto', dados_pgto=NovoPagamento.__dict__):
            send_serial_cmd('SUCESSO')
            etapa = 3
        else:
            send_serial_cmd('erro')
            return False

def send_serial_cmd(comando, valor=0):
    if comando in ['EXIBIR_VALOR','SOLICITA_SENHA']:
        comando = comando + str(valor)
    ser.write(comando.encode())  # Envia o comando para o Arduino
    if comando in ['SUCESSO', 'ERRO']:
        return

def enviar_para_api_2(**dados):
    print('Preparando dados...')
    if dados['rota'] == 'cadastra_cc':
        rota = API_2_URL + dados['rota']
        try:
            print('Enviando dados')
            
            response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    elif dados['rota'] == 'insere_pgto':
        rota = API_2_URL + dados['rota']
        print('Enviando dados')
        try:
            response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    elif dados['rota'] == 'valida_pgto':
        rota = API_2_URL + dados['rota']
        print('Enviando dados')
        try:
            response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
                return True
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    elif dados['rota'] == 'verificar_cartao':
        rota = API_2_URL + dados['rota']
        print('Enviando dados')
        try:
            response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
                return resultado.get('valido')
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    elif dados['rota'] == 'valida_senha':
        rota = API_2_URL + dados['rota']
        print('Enviando dados')
        try:
            response = requests.post(rota, json=dados) # Faz a requisição POST para a API SERVER
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
                return resultado.get('valido')
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    while True:
        input('Dados enviados pressione Enter para continuar')
        break

def processar_json(json_string):
    try:
        return json.loads(json_string)
        # Continue com o processamento dos dados...
    except json.JSONDecodeError:
        print(f"Erro ao decodificar: {json_string}")

def monitorar_serial(origem):
    while True:
        if ser.in_waiting > 0:
            dados = ser.readline().decode('utf-8').strip()
            try:
                data_dict = json.loads(dados)
                print(data_dict)
                print(type(data_dict))
                if origem == 'cad_cartao':
                    id_cartao = data_dict.get('hx_cartao')
                    return id_cartao
                elif origem == 'pag_mag':
                    return data_dict
                return
            except json.JSONDecodeError:
                print(f"Erro ao decodificar: {dados}")
                return

def menu_cmd(op_erro):
    os.system('cls')
    if op_erro:
        print("OPERAÇÃO INVÁLIDA\n")
    print("Selecione a operação:\n1- Cadastro\n2- Compra\n0- Encerrar\nOperação:")

def menu_gerenciamento(op):
    try: 
        operacao = int(op)
    except:
        return True
    if operacao == 1:
        cadastra_cartao()
        return False
    elif operacao == 2:
        pagamento()
        return False
    elif operacao == 0:
        sys.exit(0)
    else:
        return True

def main():
    ctrl_menu = False
    while True:
        menu_cmd(ctrl_menu)
        while True:
            if ser.in_waiting:
                dados = monitorar_serial(origem='pag_mag')
                os.system('cls')
                print("RECEBENDO DADOS DE PAGAMENTO...")
                print(dados)
                on_ciclo = ciclo_maquininha(data_dict=dados, etapa=1)
                if not on_ciclo:
                    break
                dados = monitorar_serial(origem='pag_mag')
                print("VALIDANDO DADOS DE PAGAMENTO...")
                on_ciclo = ciclo_maquininha(data_dict=dados, etapa=2)
                if not on_ciclo:
                    break
                ctrl_menu = False
                break
            time.sleep(0.1)
            if msvcrt.kbhit():
                operacao = input()  # Recolhe a operação
                ctrl_menu = menu_gerenciamento(operacao)
                break

if __name__ == "__main__":
    main()