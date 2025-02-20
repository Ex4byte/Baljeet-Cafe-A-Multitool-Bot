from discord.ext import commands


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignoriere Nachrichten des Bots
        if message.author == self.bot.user:
            return

        # Hier könntest du die Logik für das Leveln hinzufügen
        # (z.B. Speichern der Erfahrung und Leveln basierend auf der Nachrichtenzahl)

        # Zum Testen einfach eine Nachricht senden:
        await message.channel.send(f'{message.author.name} hat eine Nachricht gesendet!')


# Cog registrieren
def setup(bot):
    bot.add_cog(Levels(bot))
