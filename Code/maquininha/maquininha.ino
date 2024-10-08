#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>
#include <ArduinoJson.h>

//-----------------------------------------------------------------------------------------------------------------------------------
//Constantes e variáveis globais do programa-----------------------------------------------------------------------------------------
#define col 16 // Serve para definir o numero de colunas do display utilizado
#define lin  2 // Serve para definir o numero de linhas do display utilizado
#define ende  0x27 // Serve para definir o endereço do display.
#define SS_PIN 10 // Serve para definir o pino de comunicação SS
#define RST_PIN A0 // Serve para definir o pino de comunicação RST
const byte numLinhas = 4; //Quantidade de linhas do teclado
const byte numColunas = 4; //Quantidade de colunas do teclado

String dadosCadastro = "";
String dadosPagamento = "";
String comando = "";
bool api_on = false;
String ref_1 = ""; //texto de referencia para a linha 1 do display
String ref_2 = ""; //texto de referencia para a linha 1 do display
float valor = 0;
char teclasMatriz[numLinhas][numColunas] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte pinosLinhas[numLinhas] = {5, 4, 3, 2}; //Pinos das linhas
byte pinosColunas[numColunas] = {9, 8, 7, 6}; //Pinos das Colunas
Keypad meuteclado = Keypad(makeKeymap(teclasMatriz), pinosLinhas, pinosColunas, numLinhas, numColunas);
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Cria a instância MFRC522
LiquidCrystal_I2C lcd(ende,col,lin); // Chamada da funcação LiquidCrystal para ser usada com o I2C


//-----------------------------------------------------------------------------------------------------------------------------------
// Métodos de controle das etapas de pagamento a partir da maquininha----------------------------------------------------------------
/*typedef bool (*CPM)();
CPM metodos[] = {cpmFormaPagamento, cpmValorPagamento, cpmLeituraCartao, cpmLeituraSenha, cpmFaturaPagamento};

//Métodos slaves
bool cpmFormaPagamento(){}
bool cpmValorPagamento(){}
bool cpmLeituraCartao(){}
bool cpmLeituraSenha(){}
bool cpmFaturaPagamento(){}

//Método mestre
void cpmCicloPagamentoMaquininha(){
  for (int i = 0; i < 5; i++) {
    if (!metodos[i]()) {
      
      break;  // Interrompe o ciclo se o método retornar false
    }
  }
}*/

//-----------------------------------------------------------------------------------------------------------------------------------
//Método para leitura do cartão retorna uma string com ID do cartão------------------------------------------------------------------
String lerCartao(){
  String content = "";
  while (true){
    if(mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()){
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
        content.concat(String(mfrc522.uid.uidByte[i], HEX));
      }
      content.toUpperCase();
      return content;
    }
    delay(1000);
  }
}

//Método que recebe dados pelo serial da API=======================================================================================
bool apiSerial(){
  String cartao;
  while(true){
    if(Serial.available() > 0){
      comando = Serial.readStringUntil('\n');
      break;
    }
  }
  if (comando == "CADASTRAR_CARTAO"){
    display("APROX. O CARTAO", " PARA CADASTRO");
    cartao = lerCartao();
    dadosCadastro = "{\"hx_cartao\":\"" + cartao + "\"}";
    serialApi(dadosCadastro);
    display("CADASTRANDO", cartao);
    return true;
  }
  else if (comando.startsWith("EXIBIR_VALOR")){
    String valor = comando.substring(12);
    display("Valor: " + valor, "Aproxime o cartao");
    cartao = lerCartao();
    display("Processando", cartao);
    dadosPagamento = "{\"hx_cartao\":\"" + cartao + "\"}";
    serialApi(dadosPagamento);
    return true;
  }
  else if(comando == "SUCESSO"){
    api_on = false;
    return true;
  }
  else if(comando == "ERRO"){
    api_on = false;
    return false;
  }
}

//==================================================================================================================================
//=====================================                 SETUP                             ==========================================
//==================================================================================================================================
void setup() {  
  lcd.init(); // Serve para iniciar a comunicação com o display já conectado
  lcd.backlight(); // Serve para ligar a luz do display
  lcd.clear(); // Serve para limpar a tela do display
  Serial.begin(9600);   // Inicia a comunicação serial
  SPI.begin();          // Inicia SPI bus
  mfrc522.PCD_Init();   // Inicia o MFRC522
}

//==================================================================================================================================
//=====================================                   LOOP                             =========================================
//==================================================================================================================================
void loop() {
  display("DEBTS Pag", "#->p/ pagamento ");
  char pressionado = meuteclado.getKey();
  if (pressionado == '#') { //Se alguma tecla foi pressionada
    acionamentoLocal();
  }
  do{
    if(Serial.available() > 0){
      api_on = apiSerial();
    }
  }while(api_on);
}

//==================================================================================================================================
//Métodos complementares============================================================================================================
void acionamentoLocal(){
  dadosPagamento = dadosPagamento + "{\"tp_pagamento\":";
  while(true){
    display("Forma de pgto :", "A-Credto B-Debto");
    char forma_pgto = meuteclado.getKey();
    String parcelas = "";
    if(forma_pgto == 'A'){
      dadosPagamento = dadosPagamento + "1,";
      display("Parcelas:","Apag|Canc|D-Prox");
      lcd.setCursor(10, 0);
      while(true){
        char tecla = meuteclado.getKey();
        //preenchimento da senha
        if (isDigit(tecla) && (parcelas == "" || parcelas == "1")){
          parcelas = parcelas + tecla;
          lcd.print(tecla);
        }
        else if(tecla == 'C'){
          display("Operacao", "Cancelada");
          return;
        }
        else if(tecla == 'D' && parcelas != ""){
          dadosPagamento = dadosPagamento + "\"parcelas\":" + parcelas + ",";
          break;
        }
      }
      break;
    }
    else if(forma_pgto == 'B'){
      dadosPagamento = dadosPagamento + "2,";
      break;
    }
  }
  acionamentoValor();
}

//Rotina de pagamento
void acionamentoValor(){
  float valor = 0 ;
  long centavos = 0;
  String valorStr;
  while(true){
    String valorStr = String(valor, 2);
    display("Valor: " + valorStr, "Apag|Canc|D-Prox");
    char tecla = meuteclado.getKey();
    //Tratamento do valor digitado
    if (isDigit(tecla) && centavos < 100000){
      int digito = tecla - '0';
      centavos = (centavos * 10) + digito;
      valor = centavos/100.0; 
    }
    //Reseta valor
    else if (tecla == 'A' && valor > 0){
      valor = 0;
      centavos = 0;
    }
    //cacela operação
    else if(tecla == 'C'){
      display("Operacao", "Cancelada");
      delay(1000);
      break;
    }
    //Avanço de tela
    else if(tecla == 'D' && valor > 1){
      dadosPagamento = dadosPagamento + "\"valor\":" + valorStr + ",";
      String cartao;
      display("APROXIME O","CARTAO....");
      cartao = lerCartao();
      dadosPagamento = dadosPagamento + "\"hx_cartao\":\"" + cartao + "\"}";
      display("VALIDANDO","CARTAO....");
      serialApi(dadosPagamento);
      if(apiSerial()){
        //Validação da senha
        if(inserirSenha(valorStr)){
          display("Pagamento","Aprovado");
          delay(3000);
          return;
        }
        else{
          display("SENHA INVALIDA","OPER. CANCELADA");
          delay(3000);
          return;
        }
      }
      else{
        display("CARTAO INVALIDO","OPER. CANCELADA");
        dadosPagamento = "";
        return;
      }
    }
  }
}

/*Fluxo de digitar a senha*/
bool inserirSenha(String valorStr){
  String senha = "";
  display("Valor: " + valorStr, "senha:");
  lcd.setCursor(6, 1);
  //Loop para usuário digiar a senha
  while(true){
    char tecla = meuteclado.getKey();
    //preenchimento da senha
    if (isDigit(tecla) && senha.length() < 6){
      senha = senha + tecla;
      lcd.print("*");
    }
    //libera dados para API
    else if((tecla == 'D') && (senha.length() > 1)){
      display("Processando", "Aguarde...");
      dadosPagamento.replace("}", ",");
      dadosPagamento = dadosPagamento + "\"pass\":\"" + senha + "\"}";
      serialApi(dadosPagamento);
      if(apiSerial()){
        dadosPagamento="";
        return true;
      }
      else
        return false;
    }
    //Apaga senha digitada e permite tentar de novo
    else if(tecla == 'A'){
      senha = "";
      display("Valor: " + valorStr, "senha:          ");
      lcd.setCursor(6, 1);
    }
    //Cancela a operação
    else if(tecla == 'C'){
      return false;
    }
  }
}
//Metódo exibição padrão no display
void display(String linha1, String linha2){
  if (ref_1 != linha1 || ref_2 != linha2){
    ref_1 = linha1;
    ref_2 = linha2;
    lcd.clear();
    lcd.setCursor(0,0); // Coloca o cursor do display na coluna 1 e linha 1
    lcd.print(linha1); // Comando de saída com a mensagem que deve aparecer na coluna 2 e linha 1.
    lcd.setCursor(0, 1); //Coloca o cursor do display na coluna 1 e linha 2
    lcd.print(linha2);  // Comando de saida com a mensagem que deve aparecer na coluna 2 e linha 2
  }
}

//Método que envia dados pelo serial para a API=====================================================================================
void serialApi(String dados) {
  Serial.println(dados);
  delay(1000);
}
