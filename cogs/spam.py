import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class SpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Spam-Befehl mit einem schöneren Embed
    @app_commands.command(name="spam", description="Versendet Spam-Nachrichten an einen Benutzer und postet die Nachricht im Channel.")
    async def spam(self, interaction: discord.Interaction, user: discord.User, amount: int, theme: str, message: str, image_url: str):
        """Spam Befehl mit schönerem Embed-Design"""

        # Eingabekontrollen für die Anzahl der Nachrichten
        if amount < 1 or amount > 10:
            await interaction.response.send_message("Bitte gib eine Zahl zwischen 1 und 10 für die Anzahl der Nachrichten an.", ephemeral=True)
            return

        # Wähle das Thema für das Embed und die passende Farbe
        if theme == "classic":
            embed_color = discord.Color.blue()
            title = "Spam-Nachricht (Classic)"
        elif theme == "dark":
            embed_color = discord.Color.dark_gray()
            title = "Spam-Nachricht (Dark)"
        else:
            embed_color = discord.Color.purple()
            title = "Spam-Nachricht (Standard)"

        # Erstelle das Embed mit den neuen Feldern
        embed = discord.Embed(
            title=title,
            description=f"**Spam-Nachricht an {user.mention}**",  # Diese Zeile bleibt nur in der Beschreibung des Embeds
            color=embed_color
        )

        # Nachricht wird fett angezeigt
        embed.add_field(name="Nachricht", value=f"**{message}**", inline=False)

        # Profilbild des Benutzers als Thumbnail
        embed.set_thumbnail(url=user.avatar.url)

        # Bild aus der URL hinzufügen
        embed.set_image(url=image_url)

        # Footer für zusätzliche Informationen (z. B. Name des Bots)
        embed.set_footer(text=f"Gesendet von {interaction.user.name}", icon_url=interaction.user.avatar.url)

        # Timestamp hinzufügen, um den Zeitpunkt zu zeigen
        embed.timestamp = interaction.created_at

        # Sende das Embed im Kanal, in dem der Befehl ausgeführt wurde
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Spam-Nachrichten im Kanal posten
        for _ in range(amount):
            # Nachricht im Channel posten
            await interaction.channel.send(embed=embed)
            await asyncio.sleep(1)  # 1 Sekunde warten, um Spamming zu verhindern

        await interaction.followup.send(f"Ich habe {amount} Nachrichten an {user.mention} im Channel gesendet!", ephemeral=True)

# Cog wird beim Laden des Bots hinzugefügt
async def setup(bot):
    await bot.add_cog(SpamCog(bot))
