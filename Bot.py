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
              'cogs.etc']

embed = None

# Different caches for things such as sam hyde images and game sessions
covid_cache, available_games, ttt_board, hangman_states = None, None, None, None
global_image_pointer_cache, ttt_cache, hangman_cache, game_boards = dict(), dict(), dict(), dict()
words = list()

# Declare quotes, blacklist
quotes = ""
blacklist = None

# API keys, tokens (the BOT'S key cannot go here)
owm_api_key = os.environ["OWMAPIKEY"]


async def init_vars():
	# Bot characteristics
    global embed
    embed = discord.Embed(color=consts.color)
    embed.set_thumbnail(url=consts.avatar)

	# Cache, states, etc.
    global available_games
    global covid_cache
    global ttt_board
    global hangman_states
    global game_boards

    available_games = ["ttt"]
    covid_cache = ["date", 0]
    ttt_board = [['.','.','.'],['.','.','.'],['.','.','.']]
    hangman_states = await helpers.get_hm_states()
    game_boards["ttt"] = ttt_board

    # Quotes and blacklist
    global quotes
    global blacklist

    quotes = await helpers.get_quotes()
    blacklist = await helpers.get_blacklist()


# Things to run once the bot successfully authenticates
@bot.event
async def on_ready():
    print("Bot online")
    await init_vars()
    game = discord.Game("Fluffing Feathers")
    await bot.change_presence(activity=game)


# Things to run when a member joins the server
# Currently sends them a welcome message
@bot.event
async def on_member_join(member):
	embed.title = "Welcome!"
	embed.description = text.rules
	await member.send(embed=embed)


# An attempt trying to configure things upon the bot joining
# Haven't figured everything out, probably requires admin upon joining or something
@bot.event
async def on_guild_join(ctx):
    roles = [x.name for x in ctx.roles]
    if "Muted" not in roles:
        permissions = discord.Permissions(send_messages=False, read_messages=True)
        await ctx.create_role(name="Muted", permissions=permissions)

    muted = discord.utils.get(ctx.roles, name="Muted")
    for channel in ctx.channels:
        await channel.set_permissions(muted, send_messages=False, read_messages=True)

    await ctx.send(embed=embed)


for extension in extensions:
    bot.load_extension(extension)

bot.run(os.environ["UNRBOTKEY"])
