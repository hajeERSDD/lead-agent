import time
import schedule
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

META_TOKEN = os.getenv("META_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
FORM_ID = os.getenv("META_FORM_ID")

QUIET_START = 20
QUIET_END = 8
DELAY_MINUTES = 1
already_sent = set()

def get_leads():
    url = f"https://graph.facebook.com/v18.0/{FORM_ID}/leads"
    params = {"access_token": META_TOKEN}
    response = requests.get(url, params=params)
    data = response.json()
    print(f"Meta API: {data}")
    leads = []
    if "data" in data:
        for lead in data["data"]:
            phone = None
            name = "cher client"
            for field in lead.get("field_data", []):
                if "phone" in field["name"].lower():
                    phone = field["values"][0]
                if "name" in field["name"].lower() or "nom" in field["name"].lower() or "prenom" in field["name"].lower():
                    name = field["values"][0]
            if phone:
                leads.append({"id": lead["id"], "phone": phone, "name": name})
    print(f"Leads trouves: {len(leads)}")
    return leads

def send_template(phone_number, name):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {META_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "creation_site",
            "language": {"code": "fr"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": name
                        }
                    ]
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Message {phone_number} ({name}): {response.status_code} - {response.json()}")

def should_wait(hour):
    return hour >= QUIET_START or hour < QUIET_END

def process_lead(phone, lead_id, name):
    if lead_id in already_sent:
        return
    already_sent.add(lead_id)
    hour = datetime.now().hour
    if should_wait(hour):
        print(f"Nuit ({hour}h) - 9h pour {phone}")
        schedule.every().day.at("09:00").do(lambda: send_template(phone, name)).tag("pending")
    else:
        print(f"Jour ({hour}h) - {DELAY_MINUTES}min pour {phone}")
        time.sleep(DELAY_MINUTES * 60)
        send_template(phone, name)

def check_new_leads():
    print(f"Check: {datetime.now().strftime('%H:%M:%S')}")
    leads = get_leads()
    for lead in leads:
        process_lead(lead["phone"], lead["id"], lead["name"])

print("Agent demarre!")
schedule.every(5).minutes.do(check_new_leads)
check_new_leads()

while True:
    schedule.run_pending()
    time.sleep(30)
