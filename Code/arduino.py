import serial
import requests
import os
import sys
import time
import msvcrt
import hashlib

# Configura a porta serial
ser = serial.Serial('COM4', 9600)  # Use a porta correta
API_2_URL = 'http://localhost:5001/'
modelo = {1:["Crédito", True, False], 2:["Débito", False, True], 3:["Déb/Créd", True, True]}

class DadosCadastro():
    def __init__(self, hx_cartao):
        self.cd_cartao = hash_cartao(hx_cartao)
        self.hx_cartao = hx_cartao
        self.ds_titular = None
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
            if str.isalpha(titular):
                os.system('cls')
                self.ds_titular = titular
            else:
                os.system('cls')
                print("NOME INVÁLIDO\n")
    def entrada_operadora(self):
        while True:
            operadora = input("Fornecedor do cartão: ")
            if str.isalpha(operadora):
                os.system('cls')
                self.ds_operadora = operadora
                break
            else:
                os.system('cls')
                print("NOME INVÁLIDO\n")
    def entrada_tp_cartao(self):
        while True:
            tp_cartao = input("Selecione o tipo:\n1-Crédito\n2-Débito\n 3-Crédito e Débito\n=>")
            try:
                if int(tp_cartao) in modelo.keys():
                    self.tp_credito = modelo[tp_cartao][1]
                    self.tp_debito = modelo[tp_cartao][2]
                break
            except:
                print("OPÇÃO INVÁLIDA\n")
    def check_cadastro(self):
        while True:
            os.system('cls')
            confirma = input(f'Confirme os dados:\n \\
                                Titular:\t{self.ds_titular}\n \\
                                Nº Cartão:\t{self.cd_cartao}\n \\
                                Operadora:\t{self.ds_operadora}\n \\
                                Crédito:\t{'Crédito' if (self.tp_credito and not self.tp_debito) else 'Débito'} \\
                                S-SIM \ N-NÃO >>')
            if confirma.upper() == 'S':
                return True
            elif confirma.upper() == 'N':
                return False
            else:
                print('opção inválida')

class DadosPagamento():
    def __init__(self):
        self.valor = None
        self.cd_cartao = None
        self.tp_credito = None
        self.tp_debito = None
        self.senha = None
    def ciclo_pagamento(self):
        self.entrada_modo_pagamento()
        self.entrada_valor()
    def entrada_modo_pagamento(self):
        while True:
            tp_cartao = input("Selecione o tipo de pagamento:\n1-Crédito\n2-Débito")
            try:
                if int(tp_cartao) in modelo.keys() and int(tp_cartao) != 3:
                    self.tp_credito = modelo[tp_cartao][1]
                    self.tp_debito = modelo[tp_cartao][2]
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
    def check_pagamento(self):
        while True:
            os.system('cls')
            confirma = input(f'Confirme os dados:\n \\
                                Pagamento: {'Crédito' if (self.tp_credito and not self.tp_debito) else 'Débito'}\n \\
                                Valor: {self.valor}\n \\
                                S-SIM \ N-NÃO >>')
            if confirma.upper() == 'S':
                print("Aguardando cartão...")
                self.senha = send_serial_cmd('EXIBIR_VALOR', valor=self.valor)
                enviar_para_api_2(rfid_id=resposta, valor=valor, operacao=tp_cartao, rota='pagamento')
                send_serial_cmd("SUCESSO")
                break
            elif confirma.upper() == 'N':
                print('cadastro cancelado')
                send_serial_cmd("CANCELADO")
                break
            else:
                print('opção inválida')
    def check_senha(self):
        pass


def hash_cartao(id_rfid_hex):
    id_decimal = int(id_rfid_hex, 16)
    hash_val = hashlib.sha256(str(id_decimal).encode()).hexdigest()
    complemento = int(hash_val[:6], 16)
    num_cartao = str(id_decimal) + str(complemento)
    if num_cartao[0] == '0':
        num_cartao = num_cartao[::-1]
    return num_cartao

def cadastra_cartao():
    print("Aguardando cartão...")
    resposta = send_serial_cmd("\nCADASTRAR_CARTAO")
    NovoCadastro = DadosCadastro(resposta)
    os.system('cls')
    #Entrada do nome do titular
    if NovoCadastro.ciclo_cadastro():
        enviar_para_api_2(NovoCadastro)
        send_serial_cmd("SUCESSO")
    else:
        print('cadastro cancelado')
        send_serial_cmd("CANCELADO")
    
def pagamento():
    os.system('cls')
    
    
    os.system('cls')
    print("Aguardando cartão...")
    resposta = send_serial_cmd('EXIBIR_VALOR', valor=valor)
   

def send_serial_cmd(comando, valor=0):
    if comando == 'EXIBIR_VALOR':
        comando = comando + str(valor)
    ser.write(comando.encode())  # Envia o comando para o Arduino
    if comando == 'SUCESSO':
        return
    resposta = None
    while resposta is None:
        resposta = ser.readline().decode().strip()  # Lê a resposta do Arduino
    return resposta

def enviar_para_api_2(dados):
    print('Preparando dados...')

    if rfid['rota'] == 'cadastra_cc':
        dados = {'id_cartao': rfid['rfid_id'],
                'nome_titular': rfid['titular'],
                'tp_cartao': rfid['operacao']}
        rota = API_2_URL + rfid['rota']
        try:
            # Faz a requisição POST para a API SERVER
            print('Enviando dados')
            response = requests.post(rota, json=dados)
            
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    elif rfid['rota'] == 'pagamento':
        dados = {'id_cartao': rfid['rfid_id'],
                'valor': rfid['valor'],
                'tp_cartao': rfid['operacao']}
        rota = API_2_URL + rfid['rota']
        print('Enviando dados')
        try:
            # Faz a requisição POST para a API SERVER
            response = requests.post(rota, json=dados)
            
            # Verifica o status da resposta
            if response.status_code == 201:
                resultado = response.json()
                print(f">>: {resultado['mensagem']}")
            else:
                erro = response.json().get('erro', 'Erro desconhecido')
                print(f"Erro no cadastro:\n>>ERROR: {response.status_code} - {erro}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao se comunicar com a API do BD: {e}")
    while True:
        input('Dados enviados pressione Enter para continuar')
        break

def menu_cmd(op_erro):
    os.system('cls')
    if op_erro:
        print("OPERAÇÃO INVÁLIDA\n")
    print("Selecione a operação:\n1- Cadastro\n2- Compra\n0- Encerrar\nOperação:")

def monitorar_serial():
    while True:
        if ser.in_waiting > 0:
            dados = ser.readline().decode('utf-8').strip()
            dados = dados.split('@')
            os.system('cls')
            print(f"Dado recebido da maquininha:\n")
            for i, dado in enumerate(dados):
                print(f'{i} :{dado}')
            time.sleep(3)
            send_serial_cmd("SUCESSO")
        return

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
                monitorar_serial()
                ctrl_menu = False
                break
            time.sleep(0.1)
            if msvcrt.kbhit():
                operacao = input()  # Recolhe a operação
                ctrl_menu = menu_gerenciamento(operacao)
                break
            

if __name__ == "__main__":
    main()