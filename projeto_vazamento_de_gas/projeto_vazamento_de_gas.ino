#define MQ2_PIN A0    // Pino analógico conectado ao sensor de gás MQ-2

void setup() {
  Serial.begin(9600);    // Inicializa a comunicação serial
  pinMode(MQ2_PIN, INPUT);
}

void loop() {
  int gasValue = analogRead(MQ2_PIN);    // Leitura do valor do sensor de gás
  Serial.println(gasValue);   // Envia o nível de gás para o Serial
  delay(5000);    // Aguarda 5 segundos entre as leituras
}
