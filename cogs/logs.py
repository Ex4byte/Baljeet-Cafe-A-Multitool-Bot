import logging
from discord.ext import commands
from datetime import datetime

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    @commands.Cog.listener()
    async def on_message(self, message):
        logging.info(f'[{datetime.now()}] [{message.guild.name}] [{message.channel.name}] {message.author}: {message.content}')

def setup(bot):
    bot.add_cog(Logging(bot))