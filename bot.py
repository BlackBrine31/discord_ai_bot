import os
import discord
import openai
#from keep_alive import keep_alive

TOKEN = os.environ['DISCORD_TOKEN']
OPENAI_KEY = os.environ['OPENAI_KEY']

# Set up the OpenAI API client
openai.api_key = OPENAI_KEY

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(command_prefix='/', intents=intents)


chat_history = []
logged_in_user = None


def add_chat_history(chat_history, message):
  chat_history.append(message)
  chat_history = chat_history[-10:]

def format_chat_history(chat_history):
  formatted_chat_history = "\n".join(
    [f"{message.author}: {message.content}" for message in chat_history])

  return formatted_chat_history


def generate_prompt(logged_in_user, chat_history):
  prompt = f"""You are a professional healthcare AI.
You make a friendly conversation with the students. You ask them how they are doing. You give them advice and support.
You are very kind and helpful. you ask them which lessons did they have today
{format_chat_history(chat_history)}
{logged_in_user}:"""

  return prompt


@client.event
async def on_ready():
  global logged_in_user
  logged_in_user = client.user
  print('We have logged in as {0.user} in main'.format(client))


@client.event
async def on_message(message):
  print("Message Recieved")

  add_chat_history(chat_history, message)
  if message.author == client.user:
    return

  if client.user in message.mentions:
    print(f"Responding to message: {message.content}")

    prompt = generate_prompt(logged_in_user, chat_history)

    response = openai.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
      ],
      max_tokens=2048,
      temperature=0.5,
    )

    response_text = response.choices[0].message.content
    if response_text:
        response_text = response_text.strip()
        await message.channel.send(response_text)
    else:
        await message.channel.send("I apologize, but I couldn't generate a response.")

#keep_alive()

client.run(TOKEN)
