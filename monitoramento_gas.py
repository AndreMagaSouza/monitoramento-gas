import serial
import time
import paho.mqtt.client as mqtt
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da porta serial
try:
    ser = serial.Serial('COM8', 9600)  # Substitua pela porta correta
    time.sleep(2)  # Tempo para inicializar
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

# Configurações do MQTT
mqtt_broker = "demo.thingsboard.io"
mqtt_port = 1883
mqtt_topic = "v1/devices/me/telemetry"
client = mqtt.Client(client_id="ArduinoGasMonitor")

# Configurações de autenticação do ThingsBoard
token = os.getenv("MQTT_TOKEN")
client.username_pw_set(token)

# Configurações do E-mail
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")

# Callback de conexão do MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao ThingsBoard com código {rc}")

client.on_connect = on_connect

# Conectar ao broker MQTT
try:
    client.connect(mqtt_broker, mqtt_port)
except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {e}")
    exit()

# Função para enviar alerta por e-mail
def send_alert_via_email(gas_level):
    alert_message = f"ALERTA: Nível perigoso de gás detectado! Nível atual: {gas_level} ppm"
    msg = MIMEText(alert_message)
    msg["Subject"] = "Alerta de Gás Perigoso"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Alerta de gás enviado por e-mail.")
    except Exception as e:
        print(f"Erro ao enviar e-mail de alerta: {e}")

# Loop principal para monitorar o nível de gás
while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode().strip()  # Lê o valor do Arduino
        if data.isdigit():  # Verifica se o dado é numérico
            gas_level = int(data)
            print("Nível de Gás:", gas_level)

            # Preparar mensagem JSON para o ThingsBoard
            payload = '{"gasLevel": ' + str(gas_level) + '}'

            # Publicar no tópico MQTT
            client.publish(mqtt_topic, payload)

            # Enviar alerta por e-mail se o nível de gás for alto
            if gas_level > 400:
                send_alert_via_email(gas_level)

            time.sleep(5)
        else:
            print("Dado inválido recebido:", data)
