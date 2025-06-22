import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FOGOS_API = 'https://api.fogos.pt/v2/incidents/active?all=1&subRegion=Viseu%20D%C3%A3o%20Laf%C3%B5es'
INTERVALO = 120  # segundos

ocorrencias_enviadas = set()

def obter_ocorrencias():
    try:
        resposta = requests.get(FOGOS_API)
        if resposta.status_code == 200:
            dados = resposta.json()
            return [o for o in dados if o['concelho'] == "Oliveira de Frades"]
    except Exception as e:
        print(f"Erro: {e}")
    return []

def enviar_alerta(ocorrencia):
    mensagem = f"🚨 *Nova Ocorrência em Oliveira de Frades*\n\n" \
               f"🕒 *Data:* {ocorrencia['date']} às {ocorrencia['hour']}\n" \
               f"🚨 *Tipo:* {ocorrencia['natureza']}\n" \
               f"📍 *Local:* {ocorrencia['concelho']} / {ocorrencia['localidade']}\n" \
               f"📡 _Dados: Prociv / fogos.pt_"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

print("🚒 Bot de Alerta BVOFRADES iniciado...")
while True:
    ocorrencias = obter_ocorrencias()
    for o in ocorrencias:
        if o['id'] not in ocorrencias_enviadas:
            enviar_alerta(o)
            ocorrencias_enviadas.add(o['id'])
    time.sleep(INTERVALO)
