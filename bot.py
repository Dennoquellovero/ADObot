import os
import logging
from dotenv import load_dotenv
import asyncio

import discord
from discord.ext import commands

load_dotenv()

token = os.getenv('DISCORD_TOKEN')


file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Create console handler
console_handler = logging.StreamHandler()

# Configure logging with both
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


intents = discord.Intents.default() 
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='cm.', intents=intents)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load_cogs()
    if token is None:
        raise ValueError("Token is not set.")
    await bot.start(token)
    await bot.tree.sync()

asyncio.run(main())