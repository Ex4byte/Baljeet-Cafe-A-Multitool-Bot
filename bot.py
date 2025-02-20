import discord
from discord.ext import commands
import asyncio

# Intents konfigurieren
intents = discord.Intents.default()
intents.members = True  # Für Member-Informationen
intents.message_content = True  # Für Nachrichteninhalt
intents.presences = True  # Falls benötigt

bot = commands.Bot(
    command_prefix="/",
    intents=intents,
    chunk_guilds_at_startup=True  # Lädt alle Mitglieder beim Start
)


@bot.event
async def on_ready():
    """Wird beim erfolgreichen Verbindungsaufbau aufgerufen"""
    print(f'✅ {bot.user} ist online (ID: {bot.user.id})')
    print('------')

    # Cogs laden
    await load_cogs()

    # Commands syncen
    await sync_commands()


async def load_cogs():
    """Lädt alle Cogs mit Fehlerbehandlung"""
    cogs = [
        'cogs.welcome',
        'cogs.voice',
        'cogs.dmspam',
        'cogs.spam',
        'cogs.autorole'
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'🔌 Cog geladen: {cog}')
        except Exception as e:
            print(f'❌ Fehler beim Laden von {cog}: {str(e)}')


async def sync_commands():
    """Synchronisiert Commands mit Statusanzeige"""
    try:
        # Sync global und pro Guild
        global_synced = await bot.tree.sync()
        guild_synced = []

        # Für schnelleres Testing: Sync mit bestimmten Guilds
        for guild_id in []:  # Hier Guild-IDs eintragen
            guild = bot.get_guild(guild_id)
            if guild:
                await bot.tree.sync(guild=guild)
                guild_synced.append(guild.name)

        print('🔄 Command-Sync:')
        print(f'- Global: {len(global_synced)} Commands')
        if guild_synced:
            print(f'- Guilds: {", ".join(guild_synced)}')

    except Exception as e:
        print(f'🔥 Sync-Fehler: {str(e)}')


@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Manueller Sync (Nur Bot-Owner)"""
    async with ctx.typing():
        try:
            # Sync durchführen
            synced = await bot.tree.sync()

            # Response mit Details
            command_list = "\n".join([f"- {cmd.name}" for cmd in synced])
            await ctx.send(
                f"✅ **Sync erfolgreich**\n"
                f"**Commands:**\n{command_list}\n"
                f"**Anzahl:** {len(synced)}"
            )

        except Exception as e:
            await ctx.send(f"❌ **Sync fehlgeschlagen:**\n{str(e)}")


@bot.event
async def on_command_error(ctx, error):
    """Globale Fehlerbehandlung"""
    if isinstance(error, commands.NotOwner):
        await ctx.send("⛔ Dieser Befehl ist nur für den Bot-Owner!")
    else:
        print(f'⚠️ Unbehandelter Fehler: {str(error)}')


bot.run('')
