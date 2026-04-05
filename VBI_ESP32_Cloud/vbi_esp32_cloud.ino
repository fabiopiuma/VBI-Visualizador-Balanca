#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>

// Fornece informações completas sobre Addons do Firebase
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

/* 1. Definições de Rede Local (Da Fábrica / Balança) */
#define WIFI_SSID "NOME_DO_SEU_WIFI"
#define WIFI_PASSWORD "SENHA_DO_WIFI"

/* 2. Definições da Nuvem (Firebase Cloud) */
#define API_KEY "AIzaSyD9q5bLMf7ytGEMS0Z0txIZCYziI0pdk9Y"
#define DATABASE_URL "vbi-cloud-b7f78-default-rtdb.firebaseio.com"

// Objetos Principais do Firebase
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Variável para evitar flood (Enviar as coisas de tempos em tempos)
unsigned long sendDataPrevMillis = 0;
int envios_realizados = 0;

void setup() {
  Serial.begin(115200);
  
  // Conectar ao Wi-Fi Padrão do C++
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());

  // Configurar e iniciar Firebase usando o Modo Teste (Sem Autenticação Complexa para Prototipação)
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  
  // Isso desabilita as checagens rígidas de assinatura pra facilitar o primeiro boot
  config.signer.test_mode = true;
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true); // Se a balança cair, ele roda o reconectar
  
  Serial.println("Firebase 100% Injetado e pronto para a Cloud!");
}

void loop() {
  
  // Aqui dentro roda a sua mágica da balança nativa. Os seus laços de Modbus, pesagem etc.
  // ...
  // Supondo que você tem na memória local as seguintes grandezas fresquinhas:
  int vazao_calculada = rand() % 500; // Simulando um calc
  int total_parcial = 1001; 
  int total_geral = 40590;
  float velocidade = 2.45;
  bool executando = true;

  // Rotina de Cloud: Só enviamos para o Google a cada 500 milissegundos para não congestionar
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 500 || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    // ENVIO DE DADOS: Usamos os comandos "setX" para escrever e re-escrever o painel.
    // O comando formata tudo numa estrutura JSON linda chamada /balanca01/..
    
    Firebase.RTDB.setInt(&fbdo, "balanca01/vazao", vazao_calculada);
    Firebase.RTDB.setInt(&fbdo, "balanca01/total_parcial", total_parcial);
    Firebase.RTDB.setInt(&fbdo, "balanca01/total_geral", total_geral);
    Firebase.RTDB.setFloat(&fbdo, "balanca01/velocidade", velocidade);
    Firebase.RTDB.setBool(&fbdo, "balanca01/executando", executando);

    Serial.println("Tick de dados enviados para o Firebase -> Vazão: " + String(vazao_calculada));
  }
}
