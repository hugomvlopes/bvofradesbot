import requests
import time
import os
from datetime import datetime

# Variáveis de ambiente do Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FOGOS_API = 'https://api.fogos.pt/v2/incidents/active?all=1'
INTERVALO = 120  # segundos (2 minutos)

# 🔹 Funções para guardar histórico de envios
def carregar_ids():
    try:
        with open("enviados.txt", "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def guardar_id(ocorrencia_uid):
    with open("enviados.txt", "a") as f:
        f.write(f"{ocorrencia_uid}\n")

# 🔹 Função principal de alerta
def enviar_alerta(ocorrencia):
    mensagem = (
        f"*⚠️ Nova ocorrência!*\n\n"
        f"🕒 *Data:* {ocorrencia['date']} às {ocorrencia['hour']}\n"
        f"🚨 *Tipo:* {ocorrencia['natureza']}\n"
        f"📍 *Local:* {ocorrencia['concelho']} / {ocorrencia['localidade']}\n"
        f"📡 _Dados: Prociv / fogos.pt_"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}

    try:
        response = requests.post(url, data=payload)
        print(f"✅ Alerta enviado! Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar alerta: {e}")

# 🔹 Obter dados da API
def obter_ocorrencias():
    try:
        resposta = requests.get(FOGOS_API)
        if resposta.status_code == 200:
            dados = resposta.json()
            if isinstance(dados, list):
                return dados
            elif isinstance(dados, dict) and 'data' in dados:
                return dados['data']
            else:
                print("⚠️ Estrutura inesperada na resposta:", dados)
        else:
            print(f"⚠️ Erro HTTP {resposta.status_code}")
    except Exception as e:
        print(f"❌ Erro ao obter ocorrências: {e}")
    return []

# 🔹 Início do bot
print(f"🟢 BOT INICIADO: {datetime.now()}")
print("🚒 Bot de Alerta BVOFRADES [ATIVO]...")

ocorrencias_enviadas = carregar_ids()

# 🔁 Loop principal
while True:
    ocorrencias = obter_ocorrencias()
    print(f"🔍 Ocorrências recebidas: {len(ocorrencias)}")

    for o in ocorrencias:
        ocorrencia_uid = o.get('id') or f"{o['date']}|{o['hour']}|{o['concelho']}|{o['localidade']}|{o['natureza']}"
        if ocorrencia_uid not in ocorrencias_enviadas:
            enviar_alerta(o)
            ocorrencias_enviadas.add(ocorrencia_uid)
            guardar_id(ocorrencia_uid)
            time.sleep(1)  # Evitar limite da API do Telegram

    time.sleep(INTERVALO)
