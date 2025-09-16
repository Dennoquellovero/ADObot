from os import path
from discord.ext import commands
from discord import CategoryChannel, Role, StageChannel, Thread, VoiceChannel, app_commands, TextChannel, VoiceChannel
import discord, logging, json
from discord.abc import GuildChannel

logger=logging.getLogger(__name__)

class SlowModeChanger(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    slowmode_group = app_commands.Group(name="slowmode", description="Slowmode commands.")

    @slowmode_group.command(name="set", description="Set a slowmode delay for a channel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_slowmode(self, interaction: discord.Interaction, targetchannel: GuildChannel, time: int):
        logging.info(f"Setting slowmode to {time} for {interaction.guild}.")
        ##Checks that the target channel is a valid type of channel
        if isinstance(targetchannel, CategoryChannel):
            await interaction.response.send_message(f"{targetchannel.mention} cannot be a Category.", ephemeral=True)
            logging.info(f"Can't set mode for Category: {targetchannel}")
            return

        elif isinstance(targetchannel, (TextChannel, Thread, VoiceChannel, StageChannel)):
            await targetchannel.edit(slowmode_delay = time)
            await interaction.response.send_message(f"{targetchannel.mention} slowmode delay set to {time} seconds.", ephemeral=True)
            logging.info(f"Setting slowmode delay to {time} seconds for {targetchannel}")
            return

        else:
            await interaction.response.send_message("Are you sure you've input a channel?", ephemeral=True)
            logging.info("Slowmode command set to an invalid channel.")

    @slowmode_group.command(name="remove_role", description="Remove a role that can use /slowmode set.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_slowmode_roles(self, interaction: discord.Interaction, targetrole: Role):
        
        guild_id = interaction.guild_id

        path = f"serverSettings/{guild_id}.json"

        with open(path, "r") as f:
            data = json.load(f)

        logging.info(f"Attempting removal of {targetrole.mention} from {interaction.guild}")

        if targetrole.id in data["slowmode_roles"]:
            logger.info(f"Removing {targetrole.mention} from slowmode_roles for {interaction.guild}")

            data["slowmode_roles"].remove(targetrole.id)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
                await interaction.response.send_message(f"{targetrole.mention} removed from slowmode_roles", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"{targetrole.mention} not present in slowmode_roles", ephemeral=True)

    @slowmode_group.command(name="add_role", description="Add a role that can use /slowmode set")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_slowmode_roles(self, interaction: discord.Interaction, targetrole: Role):

        guild_id = interaction.guild_id

        path = f"serverSettings/{guild_id}.json"

        logging.info(f"Attempting to add {targetrole.mention} from {interaction.guild}")

        with open(path, "r") as f:
            data = json.load(f)

        if targetrole not in data["reaction_roles"]:
            logger.info(f"Adding {targetrole.mention} to slowmode_roles for {interaction.guild}")
            data["slowmode_roles"].append(targetrole.id)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
                await interaction.response.send_message(f"{targetrole.mention} can now use /slowmode set", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"{targetrole.mention} is already present.", ephemeral=True)
            return


    @slowmode_group.command(name="list_roles", description="List the roles that can use /slowmode set.")
    @app_commands.checks.has_permissions(administrator=True)            
    async def list_slowmode_roles(self, interaction: discord.Interaction):
        
        logging.info(f"Attempting to print all slowmode roles for {interaction.guild}")
    
        if interaction.guild is None:
            await interaction.response.send_message("This command must be run in a server.", ephemeral=True)
            return

        guild_id = interaction.guild_id

        path = f"serverSettings/{guild_id}.json"

        with open(path,"r") as f:
            data = json.load(f)

        slowmode_roles_list = (data["reaction_roles"])


        allowed_roles = slowmode_roles_list(guild_id)
        listed_roles = []
        for r in allowed_roles:
            stringRole = interaction.guild.get_role(int(r))
            if stringRole is not None:
                stringRole = stringRole.id 
            listed_roles.append(f"<@&{stringRole}>")
        await interaction.response.send_message(listed_roles, ephemeral=True)
        return

async def setup(bot):
    await bot.add_cog(SlowModeChanger(bot))