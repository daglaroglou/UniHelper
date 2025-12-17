import os
import nextcord
from nextcord.ext import commands, tasks

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

VERSION = "v1.0.0"

for filename in os.listdir("./commands"):
    if filename.endswith(".py"):
        bot.load_extension(f"commands.{filename[:-3]}")
        print(f"Loaded {filename}")

@tasks.loop(minutes=30)
async def change_status():
    show_version = getattr(change_status, "show_version", False)
    show_version = not show_version
    change_status.show_version = show_version

    if show_version:
        await bot.change_presence(activity=nextcord.CustomActivity(name=VERSION))
    else:
        total_users = len([filename for filename in os.listdir("./students") if filename.endswith(".json")])
        await bot.change_presence(activity=nextcord.CustomActivity(name=f"{total_users:,} students"))

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.CustomActivity(name=VERSION))
    print(f"{bot.user} is ready!")
    change_status.start()

bot.run(os.getenv("BOT_TOKEN"))