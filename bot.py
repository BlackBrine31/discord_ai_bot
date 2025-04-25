import discord
import requests
import os
import random
import json

# Environment Tokens
DISCORD_BOT_TOKEN = os.getenv('discord')
HUGGINGFACE_API_TOKEN = os.getenv('mylittlesmartAIstoken')
MODEL = "google/flan-t5-large"

# Discord Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

Character_Persona = (""""You are a professional healthcare AI.
                        You make a friendly conversation with the students. You ask them how they are doing. You give them advice and support.
                        You are very kind and helpful."""
                    )



def query_huggingface(message):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    payload = {
        "inputs": f"{Character_Persona}\nUser: {message}\nChatBuddy:",
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1
        }
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL}",
        headers=headers, json=payload
    )
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].replace(message, "").strip()
        elif "generated_text" in result:
            return result["generated_text"]
        elif "error" in result:
            return "🕒 Model is warming up, try again soon!"
        return str(result)
    return f"❌ API Error: {response.status_code}"


async def handle_help(message):
    help_text = (
        "**📚 ChatBuddy Commands:**\n"
        "`/ai <question>` – Ask anything!\n"
        "`/aistyle <new style>` – Change my personality.\n"
        "`/joke` – Get a fun joke.\n"
        "`/motivation` – Get inspired!\n"
        "`/help` – Show this help message."
    )
    await message.channel.send(help_text)

async def handle_joke(message):
    try:
        r = requests.get("https://official-joke-api.appspot.com/random_joke")
        j = r.json()
        await message.channel.send(f"{j['setup']} — {j['punchline']}")
    except:
        await message.channel.send("⚠️ Couldn't fetch a joke!")

async def handle_motivation(message):
    try:
        r = requests.get("https://zenquotes.io/api/random")
        j = r.json()
        await message.channel.send(f"✨ {j[0]['q']} – {j[0]['a']}")
    except:
        await message.channel.send("⚠️ Motivation engine offline!")

async def handle_aistyle(message):
    new_style = message.content[8:].strip()
    if new_style:
        Character_Persona = new_style
        await message.channel.send("✅ Personality updated!")
    else:
        await message.channel.send("📝 Please provide a new personality.")

async def handle_ai(message):
    query = message.content[4:].strip()
    if not query:
        await message.channel.send("✏️ Please ask something after `/ai`.")
        return

    await message.channel.send(random.choice([
        "🤖 Thinking...",
        "🔍 Searching my brain...",
        "💡 Generating wisdom...",
        "✨ Accessing neural pathways..."
    ]))

    reply = query_huggingface(query)
    await message.channel.send(reply)




@client.event
async def on_ready():
    print(f"🤖 ChatBuddy is online as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    if content.startswith("/help"):
        await handle_help(message)
    elif content.startswith("/joke"):
        await handle_joke(message)
    elif content.startswith("/motivation"):
        await handle_motivation(message)
    elif content.startswith("/aistyle"):
        await handle_aistyle(message)
    elif content.startswith("/ai"):
        await handle_ai(message)

# Run bot
client.run(DISCORD_BOT_TOKEN)
