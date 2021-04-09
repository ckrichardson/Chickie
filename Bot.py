import asyncio
from bs4 import BeautifulSoup
from copy import deepcopy
import consts
import datetime
from datetime import datetime
from datetime import timedelta
import discord as discord
from discord.ext import commands
import hashlib
import helpers
import json
import os
import pyowm
import pytz
import random
import requests
import sys
import smtplib
import text
import time
import wikipedia


#Intents (this is necessary for the welcome message)
intents = discord.Intents.all()

# Prefix used for the bot
prefix = '>'
bot = commands.Bot(command_prefix=prefix, intents=intents, description=":3")

# Cogs
extensions = ['cogs.pictures',
              'cogs.moderation',
              'cogs.information',
              'cogs.utils',
              'cogs.games',
              'cogs.etc',
              'cogs.main']

embed = None

# Declare quotes, blacklist
quotes = ""
blacklist = list()


async def init_vars():
	# Bot characteristics
    global embed
    embed = discord.Embed(color=consts.color)
    embed.set_thumbnail(url=consts.avatar)

    # Quotes and blacklist
    global quotes
    global blacklist

    quotes = await helpers.get_quotes()
    blacklist = await helpers.get_blacklist()


for extension in extensions:
    bot.load_extension(extension)

bot.run(os.environ["UNRBOTKEY"])
