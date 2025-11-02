import logging, discord, emoji, json
from discord.ext import commands
from discord import app_commands

EMOJIS = emoji.EMOJI_DATA

logger=logging.getLogger(__name__)

def reaction_roles_list(guild_id: int):
    path = "serverSettings/" + str(guild_id) + ".json"
    with open(path, "r") as f:
        data = json.load(f)
    return list(data["reaction_roles"])

class MentionReactor(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.guild is None or message.reference is not None:
            return
        guild = message.guild.id
        path = str(f"serverSettings/{guild}.json")

        with open(path, "r") as f:
            data = json.load(f)
        user_emojis = data.get("user_emojis", {})  # returns a dict

        if message.author == self.bot.user:
            return

        for user in message.mentions:
            logger.info(f"{user.id} mention found!") 

            if str(user.id) in list(user_emojis.keys()):
                emoji = user_emojis.get(str(user.id))
                await message.add_reaction(emoji)
                logger.info(f"Added 🐱 reaction for {user.id}")
                break 

        await self.bot.process_commands(message)

    # COMMANDS -----------------
    
    reaction_group = app_commands.Group(name="reaction", description="Mention to reactions commands.")

    @reaction_group.command(name="list_roles", description="List roles that can use /set mentionemoji")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_mentionroles(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        logger.info(f"Outputting reaction_roles for {guild_id}")

        allowed_roles = reaction_roles_list(guild_id)

        listed_roles = []
        for r in allowed_roles:
            stringRole = interaction.guild.get_role(int(r))
            if stringRole is not None:
                stringRole = stringRole.id 
            listed_roles.append(f"<@&{stringRole}>")
        await interaction.response.send_message(listed_roles, ephemeral=True)
        return
    
    @reaction_group.command(name="add_roles", description="Add roles that can use /set mentionemoji")
    @app_commands.describe(role="The role you want to add.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_mentionroles(self, interaction: discord.Interaction, role: str):
       
        if interaction.guild is None:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id

        role_id = role.split("&")[-1].replace(">","")

        role_exists=False
        for e in interaction.guild.roles:
            if int(e.id) == int(role_id):
                logger.debug(f"{role_id} found in {guild_id}")
                role_exists=True
                break

        if role_exists == False: 
            await interaction.response.send_message(f"{role} not found.", ephemeral=True)
            return

        role = role_id

        result = self.add_mention(guild_id, role)

        await interaction.response.send_message(f"<@&{role}> {result}", ephemeral=True)

    def add_mention(self, guild_id: int, role: str,):

        path = f"serverSettings/{guild_id}.json"

        with open(path, "r") as f:
            data = json.load(f)

        if role not in data["reaction_roles"]:
            logger.info(f"Adding {role} to reaction_roles for {guild_id}")
            data["reaction_roles"].append(role)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
                return "added to reaction mention roles."
        else:
            return "is already present."

    @reaction_group.command(name="remove_role", description="Remove roles that can use /set mentionemoji")
    @app_commands.describe(role="The role you want to remove.")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_mentionroles(self, interaction: discord.Interaction, role: str):
       
        if interaction.guild is None:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id

        role_id = role.split("&")[-1].replace(">","")

        role_exists=False
        for e in interaction.guild.roles:
            if int(e.id) == int(role_id):
                logger.debug(f"{role_id} found in {guild_id}")
                role_exists=True
                break

        if role_exists == False: 
            await interaction.response.send_message(f"{role} not found in the server.", ephemeral=True)
            return

        role = role_id

        result = self.add_mention(guild_id, role)

        await interaction.response.send_message(f"<@&{role}> {result}", ephemeral=True)

    def remove_mention(self, guild_id: int, role: str,):
        path = f"serverSettings/{guild_id}.json"

        with open(path, "r") as f:
            data = json.load(f)

        if role in data["reaction_roles"]:
            logger.info(f"Removing {role} from reaction_roles for {guild_id}")
            data["reaction_roles"].remove(role)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
                return "remove to reaction mention roles."
        else:
            return "is not present."

    @reaction_group.command(name="set_emoji", description="Set a reaction emoji on your mentions. Type 'None' to remove it.")
    @app_commands.describe(emoji="The emoji you want to set.")
    async def mentionemoji(self, interaction: discord.Interaction, emoji: str):
        
        if interaction.guild is None:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id

        member = interaction.guild.get_member(interaction.user.id)

        if member is None:
            await interaction.response.send_message("This command must be used by a user.", ephemeral=True)
            return

        member_roles = [role.id for role in member.roles]

        allowed_roles = reaction_roles_list(guild_id)

        if interaction.user.id != 210335883574902784 and not any(int(r) in member_roles for r in allowed_roles) and not member.guild_permissions.administrator:
            await interaction.response.send_message("You have no permission to run this command.", ephemeral=True)
            return

        unicode_emoji = False
        custom_emoji = False
        
        emoji = emoji.strip()

        if emoji in list(EMOJIS):
            logger.info("Unicode emoji found")
            unicode_emoji = True
        
        else:
            emoji_id = str(emoji.split(":")[-1].replace(">", ""))

            for e in interaction.guild.emojis:
                if e.id == int(emoji_id):
                    custom_emoji=True
                    logger.debug("Emoji found")
                    break

        if custom_emoji == False and unicode_emoji == False and str(emoji) != "None" and str(emoji != "none"):
            await interaction.response.send_message("You must use an emoji from this server or a stock emoji.", ephemeral=True)
            return

        elif custom_emoji == True or unicode_emoji == False or str(emoji) != "None" or str(emoji != "none"):
            msg = self.setemoji(guild_id, interaction.user.id, emoji)

        else:
            await interaction.response.send_message(f"Invalid Input.", ephemeral=True)
            return

        await interaction.response.send_message(f"{msg}", ephemeral=True)
        return

    def setemoji(self, guild_id: int, user_id: int, emoji: str, group: str = "user_emojis"):
        
        logger.debug("Setting user emojis")
        path = f"serverSettings/{guild_id}.json"

        with open(path, "r") as f:
            data = json.load(f)
        if not emoji or emoji.lower() == "none":
            if str(user_id) in data["user_emojis"]:
                del data["user_emojis"][str(user_id)]
                with open(path, "w") as f:
                    json.dump(data, f, indent = 4)
                return "Reaction emoji removed."
            else:
                return "User not set."
        else:
            data["user_emojis"][str(user_id)] = emoji
            with open(path, "w") as f:
                json.dump(data, f, indent = 4)
            return "Reaction emoji set."

async def setup(bot):
    await bot.add_cog(MentionReactor(bot))