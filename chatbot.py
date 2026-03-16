import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
messages = []

print("Chatbot prêt ! Tape 'quit' pour arrêter.")

while True:
    user_input = input("Toi: ")
    
    if user_input == "quit":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=messages
    )
    
    reply = response.content[0].text
    messages.append({"role": "assistant", "content": reply})
    
    print(f"Claude: {reply}")