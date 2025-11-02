from os import path
from discord.ext import commands
from discord import CategoryChannel, Role, StageChannel, Thread, VoiceChannel, app_commands, TextChannel, VoiceChannel 
import discord, logging, json
from discord.abc import GuildChannel

# This Cog handles setting slowmode in channels

logger=logging.getLogger(__name__)

class SlowModeChanger(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    slowmode_group = app_commands.Group(name="slowmode", description="Slowmode commands.")

    # Set the slowmode in a channel
    @slowmode_group.command(name="set", description="Set a slowmode delay for a channel.")
    async def set_slowmode(self, interaction: discord.Interaction, targetchannel: GuildChannel, time: int):

        # Check that the command is run in a server
        if interaction.guild_id == None or interaction.guild == None:
            await interaction.response.send_message("This command must be run in a server.", ephemeral=True)
            return  

        logging.info(f"Attempting to set slowmode to {time} for {interaction.guild}.")

        # Get the member component
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("This command must be run by a user.", ephemeral=True)
            return 

        # Get the member's roles and the allowed roles for the command, if no item exists in both, exit
        member_roles = [role.id for role in member.roles]

        slowmode_roles_list = self.get_slowmode_roles(interaction.guild_id)

        if not list(set(member_roles) & set(slowmode_roles_list)):
            await interaction.response.send_message("You don't have permission to run this command.", ephemeral=True)
            logging.info(f"{member} does not have any allowed roles.")
            return

        # Check that the target channel is a valid type of channel
        if isinstance(targetchannel, CategoryChannel):
            await interaction.response.send_message(f"{targetchannel.mention} cannot be a Category.", ephemeral=True)
            logging.info(f"Can't set mode for Category: {targetchannel}")
            return

        elif isinstance(targetchannel, (TextChannel, Thread, VoiceChannel, StageChannel)):
            await targetchannel.edit(slowmode_delay = time)
            await interaction.response.send_message(f"{targetchannel.mention} slowmode delay set to {time} seconds.", ephemeral=True)
            logging.info(f"Setting slowmode delay to {time} seconds for {targetchannel}")
            return

        # Handle exceptions
        else:
            await interaction.response.send_message("Are you sure you've input a channel?", ephemeral=True)
            logging.info("Slowmode command set to an invalid channel.")
            return

    # Remove slowmode roles for admin only
    @slowmode_group.command(name="remove_role", description="Remove a role that can use /slowmode set.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_slowmode_roles(self, interaction: discord.Interaction, targetrole: Role):
        
        guild_id = interaction.guild_id

        # The allowed roles are stored in a json
        path = f"serverSettings/{guild_id}.json"

        with open(path, "r") as f:
            data = json.load(f)
        logging.info(f"Attempting removal of {targetrole.mention} from {interaction.guild}")

        # If the role is in the file, remove it
        if targetrole.id in data["slowmode_roles"]:
            logger.info(f"Removing {targetrole.mention} from slowmode_roles for {interaction.guild}")
            data["slowmode_roles"].remove(targetrole.id)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
                await interaction.response.send_message(f"{targetrole.mention} removed from slowmode_roles", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"{targetrole.mention} not present in slowmode_roles", ephemeral=True)
            logger.info(f"{targetrole.mention} is not allowed roles list for {interaction.guild}.")
            return

    # Add roles to the allowed list, for admins only
    @slowmode_group.command(name="add_role", description="Add a role that can use /slowmode set")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_slowmode_roles(self, interaction: discord.Interaction, targetrole: Role):

        guild_id = interaction.guild_id

        # The allowed roles are stored in a json
        path = f"serverSettings/{guild_id}.json"

        logging.info(f"Attempting to add {targetrole.mention} from {interaction.guild}")

        with open(path, "r") as f:
            data = json.load(f)

        # If the role is not in the file, add it
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

    # Print a list of allowed roles, for admins only
    @slowmode_group.command(name="list_roles", description="List the roles that can use /slowmode set.")
    @app_commands.checks.has_permissions(administrator=True)            
    async def list_slowmode_roles(self, interaction: discord.Interaction):
        
        logging.info(f"Attempting to print all slowmode roles for {interaction.guild}")
    

        if interaction.guild_id == None or interaction.guild == None:
            await interaction.response.send_message("This command must be run in a server.", ephemeral=True)
            return 

        guild_id = interaction.guild_id

        slowmode_roles_list = self.get_slowmode_roles(guild_id)

        listed_roles = []
        for r in slowmode_roles_list:
            stringRole = interaction.guild.get_role(int(r))
            if stringRole is not None:
                stringRole = stringRole.id 
            listed_roles.append(f"<@&{stringRole}>")
        await interaction.response.send_message(listed_roles, ephemeral=True)
        return

    # A reusable function for getting the list of roles that can use the slowmode
    def get_slowmode_roles(self, guild_id: int):
        
        path = f"serverSettings/{guild_id}.json"

        with open(path,"r") as f:
            data = json.load(f)

        roles = []
        for a in data["reaction_roles"]: 
            roles.append(int(a))

        return roles

async def setup(bot):
    await bot.add_cog(SlowModeChanger(bot))