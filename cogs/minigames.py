import discord
from discord import app_commands
from discord.ext import commands
import random


class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_data = {}  # Speichert das Kapital und den Status der Benutzer

    # Funktion, um den Geldbetrag eines Benutzers zu bekommen
    def get_balance(self, user_id):
        return self.users_data.get(user_id, {'balance': 100})['balance']

    # Befehl: Arbeiten (User verdient Geld)
    @app_commands.command(name="work", description="Arbeiten, um Geld zu verdienen.")
    async def work(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)

        # Benutzer verdient zufällig zwischen 10 und 50 Münzen durch Arbeit
        earned = random.randint(10, 50)
        self.users_data[user_id] = {'balance': balance + earned}

        await interaction.response.send_message(
            f"Du hast {earned} Münzen durch Arbeit verdient! Dein neues Kapital beträgt {balance + earned} Münzen.")

    # Befehl: Investieren (User kann in den Markt investieren)
    @app_commands.command(name="invest", description="Investiere in den Markt.")
    async def invest(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)

        # Wenn der Benutzer nicht genug Geld hat
        if balance < 50:
            await interaction.response.send_message(
                f"Du hast nicht genug Geld, um zu investieren. Du hast nur {balance} Münzen.")
            return

        # Benutzer investiert
        investment_result = random.choice(["gewonnen", "verloren"])
        if investment_result == "gewonnen":
            profit = random.randint(30, 100)
            self.users_data[user_id] = {'balance': balance + profit}
            await interaction.response.send_message(
                f"Du hast in den Markt investiert und {profit} Münzen gewonnen! Dein neues Kapital beträgt {balance + profit} Münzen.")
        else:
            loss = random.randint(20, 50)
            self.users_data[user_id] = {'balance': balance - loss}
            await interaction.response.send_message(
                f"Du hast in den Markt investiert, aber leider {loss} Münzen verloren. Dein neues Kapital beträgt {balance - loss} Münzen.")

    # Befehl: Zeige den Kontostand des Benutzers
    @app_commands.command(name="balance", description="Zeigt den Kontostand an.")
    async def balance(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)
        await interaction.response.send_message(f"Dein aktueller Kontostand beträgt {balance} Münzen.")


# Cog wird beim Laden des Bots hinzugefügt
async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
