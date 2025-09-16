import logging, json, os 
from discord.ext import commands

logger=logging.getLogger(__name__)

settings = {"user_emojis": dict, "reaction_roles": list, "slowmode_roles": list}

#COMMANDS


class bootFunctions(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.settings_handler()

    @commands.Cog.listener()
    async def on_ready(self):        

        self.settings_handler()

        logger.info("Bot has started up!!")

    def settings_handler(self):
        for guild in self.bot.guilds:
            path = "serverSettings/" + str(guild.id) + ".json"
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    logger.info(f"{guild.id} settings found, loading it.")
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
                logger.info(f"Creating settings file for {guild.id}")
            
            for key in list(settings):
                if key not in data:
                    if settings[key] == dict:
                        data[key] = {}
                    elif settings[key] == list:
                        data[key] = []
                    logger.info(f"{key} missing from {guild.id}, adding it.")
            
            with open(path, "w") as f:
                json.dump(data, f, indent=4)

async def setup(bot):
    await bot.add_cog(bootFunctions(bot))