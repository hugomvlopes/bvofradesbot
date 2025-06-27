import os
import requests
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

OCORRENCIAS_URL = "https://api.fogos.pt/v2/incidents/active?all=1&subRegion=Viseu%20D%C3%A3o%20Laf%C3%B5es"
ocorrencias_enviadas = set()

print(f"\n🚒 Bot de Alerta BVOFRADES [MODO TESTE] iniciado...")

def enviar_alerta(ocorrencia):
    mensagem = (
        f"*⚠️ Nova ocorrência!*\n"
        f"🕒 *Data:* {ocorrencia['date']} às {ocorrencia['hour']}\n"
        f"🚨 *Tipo:* {ocorrencia['natureza']}\n"
        f"📍 *Local:* {ocorrencia['concelho']} / {ocorrencia['localidade']}\n"
        f"📡 _Dados: Prociv / fogos.pt_\n"
        f"💬 _Esta mensagem é automática | @bvofrades_"
    )
    payload = {
        'chat_id': CHAT_ID,
        'text': mensagem,
        'parse_mode': 'Markdown'
    }
    res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    print(f"✅ Alerta enviado! Status: {res.status_code}")

def verificar_ocorrencias():
    try:
        res = requests.get(OCORRENCIAS_URL)
        data = res.json()
        print("DEBUG DATA:", data)

        ocorrencias = data if isinstance(data, list) else data.get("data", [])
        novas_ocorrencias = [o for o in ocorrencias if isinstance(o, dict) and o['id'] not in ocorrencias_enviadas]
        print(f"🔍 Ocorrências recebidas: {len(novas_ocorrencias)}")

        for o in novas_ocorrencias:
            ocorrencias_enviadas.add(o['id'])
            enviar_alerta(o)
    except Exception as e:
        print(f"❌ Erro ao verificar ocorrências: {e}")

def verificar_e_enviar_pir():
    try:
        DICO = "1810"
        res = requests.get("https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json")
        dados = res.json()

        rcm = dados['local'][DICO]['data']['rcm']
        if rcm not in [4, 5]:
            print(f"[{datetime.now()}] RCM = {rcm} (sem envio)")
            return

        nivel = "Muito Elevado" if rcm == 4 else "Máximo"
        imagem = "https://i.imgur.com/DIZs1sq.png" if rcm == 4 else "https://i.imgur.com/GL2ir8l.png"

        legenda = (
            f"🔥 *Perigo de Incêndio Rural*\n"
            f"📍 Oliveira de Frades\n"
            f"⚠️ *Nível:* {nivel} ({rcm})\n"
            f"📡 _Fonte: IPMA (www.ipma.pt)_"
        )

        payload = {
            'chat_id': CHAT_ID,
            'photo': imagem,
            'caption': legenda,
            'parse_mode': 'Markdown'
        }

        telegram_res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)

        print(telegram_res.text)  # Debug do erro

        if telegram_res.status_code == 200:
            print(f"✅ PIR enviado com sucesso! ({nivel})")
        else:
            print(f"❌ Erro ao enviar PIR. Status: {telegram_res.status_code}")

    except Exception as e:
        print(f"❌ Erro ao verificar PIR: {e}")

# Agendamento
schedule.every(2).minutes.do(verificar_ocorrencias)
schedule.every().day.at("09:30").do(verificar_e_enviar_pir)

print("🕒 Agendamentos ativos: Ocorrências a cada 2 min | PIR às 10h")

# Execução forçada para teste
verificar_e_enviar_pir()

while True:
    schedule.run_pending()
    print(f"⏳ A correr... {datetime.now()}")
    time.sleep(30)
