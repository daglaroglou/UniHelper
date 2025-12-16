import os
import nextcord
from nextcord.ext import commands

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

for filename in os.listdir("./commands"):
    if filename.endswith(".py"):
        bot.load_extension(f"commands.{filename[:-3]}")
        print(f"Loaded {filename}")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")

bot.run(os.getenv("BOT_TOKEN"))