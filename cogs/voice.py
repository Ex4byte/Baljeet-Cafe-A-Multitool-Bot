import discord
from discord.ext import commands
from discord import app_commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Logging function for admins
    async def log_action(self, action, channel):
        log_channel = discord.utils.get(channel.guild.text_channels, name="voice-log")
        if log_channel:
            embed = discord.Embed(
                title=f"Aktion: {action}",
                description=f"**Kanal:** {channel.name}\n**Durchgeführt von:** {channel.guild.owner}",
                color=discord.Color.green()
            )
            embed.set_footer(text="Automatisch generierter Log")
            await log_channel.send(embed=embed)
        else:
            print("Kein Logs-Kanal gefunden!")

    # Autocomplete for voice-limit command
    async def limit_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[int]]:
        common_limits = [1, 2, 5, 10, 20, 50]
        return [
            app_commands.Choice(name=str(limit), value=limit)
            for limit in common_limits if current.lower() in str(limit)
        ]

    # Autocomplete for voice-rename command
    async def rename_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        common_names = ["General", "Music", "Gaming", "Study", "Meeting", "Chill"]
        return [
            app_commands.Choice(name=name, value=name)
            for name in common_names if current.lower() in name.lower()
        ]

    # Autocomplete for voice-transfer command
    async def transfer_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel:
            members = channel.members
            return [
                app_commands.Choice(name=member.name, value=str(member.id))
                for member in members if current.lower() in member.name.lower()
            ]
        return []

    # When a user joins a specific voice channel
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        trigger_channel_name = "Kanal Erstellen"

        if after.channel and after.channel.name == trigger_channel_name and before.channel != after.channel:
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(connect=True),
                member: discord.PermissionOverwrite(connect=True)
            }

            temp_channel = await member.guild.create_voice_channel(
                name=f"{member.name} Kanal",
                overwrites=overwrites,
                category=after.channel.category
            )

            await temp_channel.set_permissions(member, overwrite=discord.PermissionOverwrite(manage_channels=True, connect=True))
            await member.move_to(temp_channel)
            await self.log_action(f"{member.name} hat einen temporären Sprachkanal erstellt", temp_channel)
            embed = discord.Embed(
                title="Neuer Temporärer Kanal",
                description=f"{member.mention} ist jetzt im temporären Sprachkanal: {temp_channel.mention}!",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await temp_channel.send(embed=embed)

        elif before.channel and before.channel.name.startswith(member.name) and after.channel != before.channel:
            try:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    await self.log_action(f"Leerer temporärer Sprachkanal {before.channel.name} wurde gelöscht", before.channel)
            except discord.NotFound:
                print(f"Der Kanal {before.channel.name} wurde bereits gelöscht oder existiert nicht mehr.")

    # voice-limit command with autocomplete
    @app_commands.command(name="voice-limit", description="Set a user limit for the voice channel.")
    @app_commands.describe(limit="The maximum number of users allowed in the channel.")
    @app_commands.autocomplete(limit=limit_autocomplete)
    async def voice_limit(self, interaction: discord.Interaction, limit: int):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.edit(user_limit=limit)
            embed = discord.Embed(
                title="Nutzerlimit gesetzt",
                description=f"Das Nutzerlimit des temporären Sprachkanals wurde auf {limit} gesetzt.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-rename command with autocomplete
    @app_commands.command(name="voice-rename", description="Rename the voice channel.")
    @app_commands.describe(new_name="The new name for the voice channel.")
    @app_commands.autocomplete(new_name=rename_autocomplete)
    async def voice_rename(self, interaction: discord.Interaction, new_name: str):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.edit(name=new_name)
            embed = discord.Embed(
                title="Kanal umbenannt",
                description=f"Der temporäre Sprachkanal wurde umbenannt zu {new_name}.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-transfer command with autocomplete
    @app_commands.command(name="voice-transfer", description="Transfer ownership of the voice channel.")
    @app_commands.describe(new_owner="The new owner of the voice channel.")
    @app_commands.autocomplete(new_owner=transfer_autocomplete)
    async def voice_transfer(self, interaction: discord.Interaction, new_owner: str):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            new_owner_member = interaction.guild.get_member(int(new_owner))
            if new_owner_member:
                await channel.edit(owner=new_owner_member)
                embed = discord.Embed(
                    title="Kanal übertragen",
                    description=f"Die Eigentumsrechte des temporären Sprachkanals wurden an {new_owner_member.mention} übertragen.",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=new_owner_member.avatar.url)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Der angegebene Benutzer konnte nicht gefunden werden.", ephemeral=True)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-lock command
    @app_commands.command(name="voice-lock", description="Lock the voice channel.")
    async def voice_lock(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(interaction.guild.default_role, overwrite=discord.PermissionOverwrite(connect=False))
            embed = discord.Embed(
                title="Kanal gesperrt",
                description=f"Der temporäre Sprachkanal wurde gesperrt.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-unlock command
    @app_commands.command(name="voice-unlock", description="Unlock the voice channel.")
    async def voice_unlock(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(interaction.guild.default_role, overwrite=None)
            embed = discord.Embed(
                title="Kanal entsperrt",
                description=f"Der temporäre Sprachkanal wurde entsperrt.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-hide command
    @app_commands.command(name="voice-hide", description="Hide the voice channel.")
    async def voice_hide(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            embed = discord.Embed(
                title="Kanal ausgeblendet",
                description=f"{interaction.user.mention} hat den Kanal ausgeblendet.",
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-reveal command
    @app_commands.command(name="voice-reveal", description="Reveal the voice channel.")
    async def voice_reveal(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            embed = discord.Embed(
                title="Kanal sichtbar gemacht",
                description=f"Der temporäre Sprachkanal wurde wieder sichtbar gemacht.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-kick command
    @app_commands.command(name="voice-kick", description="Kick a user from the voice channel.")
    async def voice_kick(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels and member in channel.members:
            await member.move_to(None)
            embed = discord.Embed(
                title="User gekickt",
                description=f"{member.mention} wurde aus dem temporären Sprachkanal gekickt.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Dieser Nutzer ist nicht im Kanal oder du bist nicht der Besitzer!", ephemeral=True)

    # voice-ban command
    @app_commands.command(name="voice-ban", description="Ban a user from the voice channel.")
    async def voice_ban(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(connect=False))
            embed = discord.Embed(
                title="User gebannt",
                description=f"{member.mention} wurde vom temporären Sprachkanal gebannt.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

    # voice-unban command
    @app_commands.command(name="voice-unban", description="Unban a user from the voice channel.")
    async def voice_unban(self, interaction: discord.Interaction, member: discord.Member):
        channel = interaction.user.voice.channel if interaction.user.voice else None
        if channel and channel.permissions_for(interaction.user).manage_channels:
            await channel.set_permissions(member, overwrite=None)
            embed = discord.Embed(
                title="User entbannt",
                description=f"{member.mention} wurde vom temporären Sprachkanal entbannt.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Du bist nicht der Besitzer dieses Kanals oder bist nicht in einem Voice-Channel!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))