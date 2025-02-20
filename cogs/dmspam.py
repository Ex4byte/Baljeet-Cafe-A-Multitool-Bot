import discord
from discord import app_commands
from discord.ext import commands
import asyncio


class DmSpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Der Slash-Befehl heißt jetzt "dmspam"
    @app_commands.command(name="dmspam",
                          description="Versendet DM-Spam-Nachrichten an einen Benutzer mit verschiedenen Optionen")
    async def dmspam(self, interaction: discord.Interaction, user: discord.User, amount: int, image_url: str,
                     theme: str, message: str):
        """DM Spam Befehl mit Benutzer, Anzahl, Bild, Thema und Nachricht-Feld"""

        # Eingabekontrollen für die Anzahl der Nachrichten
        if amount < 1 or amount > 10:
            await interaction.response.send_message(
                "Bitte gib eine Zahl zwischen 1 und 10 für die Anzahl der Nachrichten an.", ephemeral=True)
            return

        # Wähle das Thema für das Embed
        if theme == "classic":
            embed_color = discord.Color.blue()
            title = "DM Spam-Nachricht (Classic)"
        elif theme == "dark":
            embed_color = discord.Color.dark_gray()
            title = "DM Spam-Nachricht (Dark)"
        else:
            embed_color = discord.Color.purple()
            title = "DM Spam-Nachricht (Standard)"

        # Erstelle das Embed mit den neuen Feldern
        embed = discord.Embed(title=title, description=f"Spam-Nachricht an {user.mention}", color=embed_color)
        embed.add_field(name="Anzahl der Nachrichten", value=f"{amount}")
        embed.add_field(name="Bild-URL", value=image_url)
        embed.add_field(name="Nachricht", value=message)  # Das Nachricht-Feld hinzufügen
        embed.set_thumbnail(url=image_url)

        # Sende das Embed als Antwort auf den Befehl
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Spam-Nachrichten senden
        for _ in range(amount):
            await user.send(f"Hey {user.name}, du hast eine Nachricht von {interaction.user.name} erhalten!")
            await user.send(embed=embed)
            await asyncio.sleep(1)  # 1 Sekunde warten, um Spamming zu verhindern

        await interaction.followup.send(f"Ich habe {amount} Nachrichten an {user.mention} gesendet!", ephemeral=True)


# Cog wird beim Laden des Bots hinzugefügt
async def setup(bot):
    await bot.add_cog(DmSpamCog(bot))
