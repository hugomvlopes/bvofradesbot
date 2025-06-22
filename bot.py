import requests
import time
import os

# Variáveis de ambiente (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# API nacional
FOGOS_API = 'https://api.fogos.pt/v2/incidents/active?all=1'
INTERVALO = 120  # segundos (2 minutos)

# Para evitar enviar ocorrências repetidas
ocorrencias_enviadas = set()

def obter_ocorrencias():
    try:
        resposta = requests.get("https://api.fogos.pt/v2/incidents/active?all=1")
        if resposta.status_code == 200:
            dados = resposta.json()
            if isinstance(dados, list):
                return dados
            else:
                print("⚠️ A resposta da API não é uma lista:", dados)
        else:
            print(f"⚠️ Erro HTTP {resposta.status_code}")
    except Exception as e:
        print(f"❌ Erro ao obter ocorrências: {e}")
    return []


def enviar_alerta(ocorrencia):
    mensagem = f"🕒 *Data:* {ocorrencia['date']} às {ocorrencia['hour']}\n" \
               f"🚨 *Tipo:* {ocorrencia['natureza']}\n" \
               f"📍 *Local:* {ocorrencia['concelho']} / {ocorrencia['localidade']}\n" \
               f"📡 _Dados: Prociv / fogos.pt_"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}

    try:
        response = requests.post(url, data=payload)
        print(f"✅ Alerta enviado! Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar alerta: {e}")

print("🚒 Bot de Alerta BVOFRADES [TESTE NACIONAL] iniciado...")
while True:
    ocorrencias = obter_ocorrencias()
    print(f"🔍 Ocorrências recebidas: {len(ocorrencias)}")

    for o in ocorrencias:
        if isinstance(o, dict) and o.get('id') and o['id'] not in ocorrencias_enviadas:
            enviar_alerta(o)
            ocorrencias_enviadas.add(o['id'])

    time.sleep(INTERVALO)
