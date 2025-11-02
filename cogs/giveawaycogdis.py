import logging, discord, pymongo
from discord.ext import commands
from discord import app_commands

logger=logging.getLogger(__name__)

class giveaways(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    giveaway_group = app_commands.Group(name="giveaway", description="Create and manage giveaways.")
    


async def setup(bot):
    await bot.add_cog(giveaways(bot))