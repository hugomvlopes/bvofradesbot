import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
import requests
import schedule
import time
from datetime import datetime

OCORRENCIAS_URL = "https://api.fogos.pt/v2/incidents/active?all=1"
ocorrencias_enviadas = set()

def verificar_ocorrencias():
    try:
        res = requests.get(OCORRENCIAS_URL)
        dados = res.json()

        if not isinstance(dados, list):
            print("❌ Dados inválidos ou vazios recebidos da API.")
            return

        ocorrencias_validas = 0

        for ocorrencia in dados:
            if ocorrencia.get("concelho", "").lower() != "oliveira de frades":
                continue

            ocorrencias_validas += 1
            ocorr_id = ocorrencia.get("id")

            if ocorr_id in ocorrencias_enviadas:
                continue

            # Enviar alerta
            enviar_alerta(ocorrencia)

            print(f"✅ Alerta enviado: ID {ocorr_id} - {ocorrencia.get('localidade')}")
            ocorrencias_enviadas.add(ocorr_id)

        print(f"🔍 Ocorrências válidas encontradas: {ocorrencias_validas}")

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
    f"⚠️ Nível: *{nivel}*\n"
    f"📡 _Fonte: IPMA (www.ipma.pt)_\n\n"
    f"🚫 Não faça uso do fogo, seja responsável!\n"
    f"🧯 A PREVENÇÃO COMEÇA EM SI. Em caso de incêndio ligue 112!"
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
