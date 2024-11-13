import discord
from discord.ext import commands
from discord_slash import SlashCommand
import json

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

bot.load_extension("cogs.money")
bot.load_extension("cogs.leaderboard")

with open("config.json", "r") as file:
    config = json.load(file)
    TOKEN = config["TOKEN"]

@bot.event
async def on_ready():
    print(f'{bot.user.name} đã sẵn sàng!')

bot.run(TOKEN)
