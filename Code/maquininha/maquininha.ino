#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>

//-----------------------------------------------------------------------------------------------------------------------------------
//Constantes e variáveis globais do programa-----------------------------------------------------------------------------------------
#define col 16 // Serve para definir o numero de colunas do display utilizado
#define lin  2 // Serve para definir o numero de linhas do display utilizado
#define ende  0x27 // Serve para definir o endereço do display.
#define SS_PIN 10 // Serve para definir o pino de comunicação SS
#define RST_PIN A0 // Serve para definir o pino de comunicação RST
const byte numLinhas = 4; //Quantidade de linhas do teclado
const byte numColunas = 4; //Quantidade de colunas do teclado

String comando = "";
String ref_1 = "";
String ref_2 = "";
float valor = 0;
char teclasMatriz[numLinhas][numColunas] = {
  {'1', '2', '3', 'A'},
  {'4', '6', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte pinosLinhas[numLinhas] = {5, 4, 3, 2}; //Pinos das linhas
byte pinosColunas[numColunas] = {9, 8, 7, 6}; //Pinos das Colunas
Keypad meuteclado = Keypad(makeKeymap(teclasMatriz), pinosLinhas, pinosColunas, numLinhas, numColunas);
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Cria a instância MFRC522
LiquidCrystal_I2C lcd(ende,col,lin); // Chamada da funcação LiquidCrystal para ser usada com o I2C

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
String getRFID() {
  String content = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  content.toUpperCase();  // Transformar em maiúsculas para consistência
  return content;
}

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
void loop() {
  display("DEBTS Pag", "#->p/ pagamento ");
  char pressionado = meuteclado.getKey();
  if (pressionado == '#') { //Se alguma tecla foi pressionada
    acionamentoLocal();
  }
  if(Serial.available() > 0){
    apiSerial();
  }
}

//==================================================================================================================================
//Métodos complementares============================================================================================================

//método de inserção de pagamento pela maquininha
void acionamentoLocal(){
  while(true){
    display("Forma de pgto :", "A-Credto B-Debto");
    char pressionado = meuteclado.getKey();
    if ((pressionado == 'A') || (pressionado == 'B')) {
      display("Valor: 0,00", "Apag|Canc|D-Prox");
      acionamentoValor(pressionado);
      break;
    }
  }
}

//Rotina de pagamento
void acionamentoValor(char op){
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
    //Avanço de tela
    else if(tecla == 'D' && valor > 1){
      String cartao;
      display("APROXIME O","CARTAO....");
      //Loop de leitura de cartão
      cartao = lerCartao()
      while(true){
        if(mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()){
          cartao = getRFID();
          break;
        }
        delay(1000);
      }
      /*
      EFETUAR PROCESSO DE VALIDAÇÃO DO CARTÃO no banco de dados
      */
      //Validação da senha
      if(inserirSenha(valorStr, cartao, op)){
        display("Pagamento","Aprovado");
        delay(3000);
        break;
      }
      else{
        display("Pagamento","Cancelado");
        delay(3000);
        break;
      }
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
  }
}

/*Fluxo de digitar a senha*/
boolean inserirSenha(String valor,String cartao,char op){
  String senha = "";
  display("Valor: " + valor, "senha:");
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
      serialApi(cartao + "@" + op + "@" + valor + "@" + senha);
      while (true){
        if(Serial.available() > 0){
          comando = Serial.readStringUntil('\n');
          if (comando == "SUCESSO"){
            return true;
          }
          else{
            return false;
          }
        }
      }
    }
    //Apaga senha digitada e permite tentar de novo
    else if(tecla == 'C'){
      senha = "";
      display("Valor: " + valor, "senha:          ");
      lcd.setCursor(6, 1);
    }
    //Cancela a operação
    else if(tecla == 'A'){
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
void serialApi(String serial_txt) {
  Serial.println(serial_txt);
  delay(2000);
}


//Método que recebe dados pelo serial da API=======================================================================================
void apiSerial(){
  comando = Serial.readStringUntil('\n');
  if (comando == "CADASTRAR_CARTAO"){
    display("APROX. O CARTAO", " PARA CADASTRO");
    while(true){
      if(mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()){
        serialApi(getRFID());
        break;
      }
      delay(1000);
    }
    display("CADASTRANDO","Aguarde");
    while (true){
      if(Serial.available() > 0){
        comando = Serial.readStringUntil('\n');
        delay(2000);
        if (comando == "SUCESSO"){
          display("Cadastro","finalizado");
          delay(3000);
          break;
        }
        else{
          display("Cadastro","Cancelado");
          delay(3000);
          break;
        }
      }
    }
  }
  else if (comando.startsWith("EXIBIR_VALOR")){
    String valor = comando.substring(12);
    display("Valor: " + valor, "Aproxime o cartão");
    while (true){
      if(mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()){
        serialApi(getRFID());
        break;
      }
    }
    display("Processando", "-----------");
    while (true){
      if(Serial.available() > 0){
        comando = Serial.readStringUntil('\n');
        delay(2000);
        if (comando == "SUCESSO"){
          display("Pagamento","Aprovado");
          delay(3000);
          break;
        }
        else{
          display("Pagamento","Cancelado");
          delay(3000);
          break;
        }
      }
    }
  }
}
