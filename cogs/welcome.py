import discord
from discord.ext import commands
import discord.utils
from datetime import datetime

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.name} ist dem Server beigetreten!")  # Debug-Ausgabe

        # Bestimmen, ob der Kanal '〔🎉〕welcome' existiert
        channel = discord.utils.get(member.guild.text_channels, name="〔🎉〕welcome")

        if channel:
            # Die Willkommensnachricht erstellen und Membercount einfügen
            welcome_message = f"Willkommen, {member.mention}! 🌟\n\n" \
                              "Schön, dass du hier bist! 😄\n\n" \
                              f"Du bist nun das {member.guild.member_count}. Mitglied! 🎉\n\n" \
                              "Bevor du loslegst, schau dir bitte unsere Regeln an und verhalte dich respektvoll!\n\n" \
                              "Falls du Fragen hast, zögere nicht, uns zu fragen! 😊"

            # Nachricht senden mit Benutzerbild, Benutzername und Serverbanner
            embed = discord.Embed(title=f"Willkommen {member.name}!", description=welcome_message,
                                  color=discord.Color.blue())

            # Überprüfen, ob der Benutzer ein Avatarbild hat
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)  # Das Avatarbild des neuen Benutzers anzeigen
            else:
                embed.set_thumbnail(url="https://i.imgur.com/4M34hi2.png")  # Fallback-Avatar (z.B. Standardbild)

            # Aktuelle Uhrzeit im Format 'HH:MM' (Stunde und Minute)
            current_time = datetime.now().strftime("%H:%M")

            # Footer mit Servername und aktueller Uhrzeit
            embed.set_footer(text=f"{member.guild.name} | {current_time} Uhr")

            # Serverbanner hinzufügen, falls verfügbar (nicht jeder Server hat ein Banner)
            if member.guild.banner:
                embed.set_image(url=member.guild.banner.url)  # Den Serverbanner setzen

            # Die Nachricht im Kanal '〔🎉〕welcome' senden
            await channel.send(embed=embed)
        else:
            print("Kein Kanal mit dem Namen '〔🎉〕welcome' gefunden.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
