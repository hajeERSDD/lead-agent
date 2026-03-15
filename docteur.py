import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
messages = []

system = """You are a virtual assistant for Dr. Ben Ali clinic.
Always respond in Modern Standard Arabic (Fusha).
Be polite and professional.

Clinic info:
- Name: Dr. Ben Ali Clinic
- Specialty: General medicine
- Address: 12 Rue de la Republique, Tunis
- Hours: Monday-Friday 8am-6pm, Saturday 8am-12pm
- Phone: 71 000 000
- Consultation fee: 40 TND

If patient wants appointment, ask for:
1. Full name
2. Preferred date
3. Phone number
Then confirm the booking."""

print("Welcome to Dr. Ben Ali Clinic Assistant")
print("Type quit to exit")
print("=" * 40)

while True:
    user_input = input("Patient: ")
    if user_input == "quit":
        break
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system,
        messages=messages
    )
    reply = response.content[0].text
    messages.append({"role": "assistant", "content": reply})
    print(f"Assistant: {reply}\n")
```

Sauvegarde en **UTF-8** et tape :
```
python docteur.py