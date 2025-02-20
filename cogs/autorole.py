import discord
from discord import app_commands
from discord.ext import commands
import json
import datetime


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        try:
            with open('autorole_config.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"role_id": None, "log_channel_id": None}

    def save_config(self):
        with open('autorole_config.json', 'w') as f:
            json.dump(self.config, f)

    async def log_action(self, action: str, member: discord.Member = None, error: str = None):
        channel = self.bot.get_channel(self.config.get('log_channel_id'))
        if not channel:
            return

        embed = discord.Embed(
            title="AutoRole Log",
            timestamp=datetime.datetime.now(),
            color=discord.Color.blue() if not error else discord.Color.red()
        )

        if member:
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)

        embed.add_field(name="Action", value=action, inline=False)

        if error:
            embed.add_field(name="Error", value=error, inline=False)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.config.get('role_id'):
            return

        try:
            role = member.guild.get_role(self.config['role_id'])
            if not role:
                await self.log_action("Role assignment failed - Role not found", member)
                return

            await member.add_roles(role, reason="AutoRole Assignment")
            await self.log_action(f"Successfully assigned role {role.name}", member)

        except discord.Forbidden:
            error = "Missing permissions to assign roles"
            await self.log_action("Role assignment failed", member, error)
        except Exception as e:
            await self.log_action("Role assignment failed", member, str(e))

    @app_commands.command(name="set_autorole", description="Set the auto-role for new members")
    @app_commands.default_permissions(administrator=True)
    async def set_autorole(self, interaction: discord.Interaction, role: discord.Role):
        self.config['role_id'] = role.id
        self.save_config()
        await interaction.response.send_message(f"✅ Auto-Role wurde auf {role.mention} gesetzt", ephemeral=True)
        await self.log_action(f"Auto-Role updated to {role.name}")

    @app_commands.command(name="set_log_channel", description="Set the log channel for autorole system")
    @app_commands.default_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.config['log_channel_id'] = channel.id
        self.save_config()
        await interaction.response.send_message(f"✅ Log-Channel wurde auf {channel.mention} gesetzt", ephemeral=True)
        await self.log_action(f"Log channel updated to {channel.name}")


async def setup(bot):
    await bot.add_cog(AutoRole(bot))