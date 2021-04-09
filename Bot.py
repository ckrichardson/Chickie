import discord as discord
from discord.ext import commands


#Intents (this is necessary for the welcome message)
intents = discord.Intents.all()

# Prefix used for the bot
prefix = '>'
bot = commands.Bot(command_prefix=prefix, intents=intents, description=":3")

# Cogs
extensions = ['cogs.main',
              'cogs.moderation',
              'cogs.information',
              'cogs.utils',
              'cogs.pictures',
              'cogs.games',
              'cogs.etc']


for extension in extensions:
    bot.load_extension(extension)

bot.run(os.environ["UNRBOTKEY"])
