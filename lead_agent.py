import schedule
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

META_TOKEN = os.getenv("META_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
FORM_ID = os.getenv("META_FORM_ID")
VOICE_NOTE_URL = os.getenv("VOICE_NOTE_URL")

QUIET_START = 20
QUIET_END = 8
DELAY_MINUTES = 20

# ✅ Fix #2: Persist already_sent to a file so restarts don't reset it
SENT_FILE = "already_sent.json"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(already_sent):
    with open(SENT_FILE, "w") as f:
        json.dump(list(already_sent), f)

already_sent = load_sent()

def get_leads():
    url = f"https://graph.facebook.com/v18.0/{FORM_ID}/leads"
    params = {
        "access_token": META_TOKEN,
        "fields": "id,field_data,created_time"  # ✅ explicitly request fields
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(f"Meta API response: {data}")
    leads = []
    if "data" in data:
        for lead in data["data"]:
            phone = None
            for field in lead.get("field_data", []):
                if "phone" in field["name"].lower():
                    phone = field["values"][0]
            if phone:
                leads.append({"id": lead["id"], "phone": phone})
    return leads

def send_voice(phone_number):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "audio",
        "audio": {"link": VOICE_NOTE_URL}
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Vocale envoye a {phone_number}: {response.status_code} - {response.json()}")

def should_wait(hour):
    return hour >= QUIET_START or hour < QUIET_END

def process_lead(phone, lead_id):
    if lead_id in already_sent:
        print(f"Lead {lead_id} deja traite, ignore.")
        return
    
    already_sent.add(lead_id)
    save_sent(already_sent)  # ✅ Fix #2: save immediately
    
    hour = datetime.now().hour
    if should_wait(hour):
        print(f"Heure tardive ({hour}h) - Vocale programme a 9h pour {phone}")
        # ✅ Fix #1: Don't sleep — schedule it non-blocking
        schedule.every().day.at("09:00").do(
            lambda p=phone: send_voice(p)
        ).tag("pending")
    else:
        print(f"Heure normale ({hour}h) - Vocale dans {DELAY_MINUTES} min pour {phone}")
        # ✅ Fix #1: Schedule for DELAY_MINUTES from now, non-blocking
        send_time = (datetime.now().replace(second=0, microsecond=0).timestamp() 
                     + DELAY_MINUTES * 60)
        send_dt = datetime.fromtimestamp(send_time).strftime("%H:%M")
        schedule.every().day.at(send_dt).do(
            lambda p=phone: send_voice(p)
        ).tag("pending")

def check_new_leads():
    print(f"Verification des leads... {datetime.now().strftime('%H:%M:%S')}")
    leads = get_leads()
    print(f"Leads trouves: {len(leads)}")
    for lead in leads:
        process_lead(lead["phone"], lead["id"])

# ✅ Fix #3: Actually schedule the repeat check
schedule.every(5).minutes.do(check_new_leads)

print("Agent Lead Meta Ads demarre !")
check_new_leads()  # run once immediately on startup

while True:
    schedule.run_pending()
    import time
    time.sleep(10)  # ✅ shorter sleep so scheduled tasks fire on time