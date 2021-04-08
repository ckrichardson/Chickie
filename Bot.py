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


# Changes the status of the bot
@commands.guild_only()
@commands.has_permissions(administrator=True)
@bot.command(pass_context=True)
async def status(ctx,*,game=None):
    game = discord.Game(str(game))
    await bot.change_presence(activity=game)


@status.error
async def status_error(ctx, error):
    embed.title="Status"
    if isinstance(error, commands.MissingPermissions):
        embed.description="You do not have the permissions to use this command"

    elif isinstance(error, commannds.CommandError):
        embed.description="Command example:\n>status looking for booty"

    await ctx.send(embed=embed)


# Sends you a motivational quote
@commands.guild_only()
@bot.command(pass_context=True)
async def quote(ctx):
    selected_quote = dict(random.choice(quotes))
    embed.title = "Quote"
    embed.description = "\"{0}\"\n-{1}".format(selected_quote["text"], selected_quote["author"])
    await ctx.send(embed=embed)


# Find out your pp size
@commands.guild_only()
@bot.command(pass_context=True)
async def pp(ctx):
    author_id = ctx.author.id
    sizes = {0: "micropenis", 1: "smol pp", 2: "regular pp", 3: "respectable pp", 4: "gargantuan pp", 5: "Chad McThundercock"}
    embed.title = "PP"
    embed.description = "<@{0}> has a `{1}`".format(author_id, sizes[[author_id % 5,5][author_id==131591965551624193]])

    await ctx.send(embed=embed)


@commands.guild_only()
@bot.command(pass_context=True)
async def insult(ctx, target: discord.Member=None):
    insult = await helpers.get_insult()
    if not target:
        msg = "<@{0}> ".format(ctx.author.id) + insult
    else:
        msg = "<@{0}> ".format(target.id) + insult
    await ctx.send(msg)


@insult.error
async def insult_error(ctx, error):
    embed.title="Insult"
    if isinstance(error, commands.BadArgument):
        embed.description = "User not found"
    
    elif isinstance(error, commands.CommandError):
        embed.description = "Command Example:\n>insult <@{0.id}>".format(ctx.author)

    await ctx.send(embed=embed)


@commands.guild_only()
@bot.command(pass_context=True)
async def info(ctx, member: discord.Member=None):
    global embed
    n_embed = deepcopy(embed)
    n_embed.set_thumbnail(url=member.avatar_url)
    n_embed.title = "Info"
    joined = member.joined_at.replace(microsecond=0) - timedelta(hours=8)
    n_embed.description = "<@{0.id}> ".format(member) + "joined on `{0}`".format(joined) + " and has been a member of this server for `{0}`".format(datetime.now().replace(microsecond=0)-joined)
    await ctx.send(embed=n_embed) 


@info.error
async def info_error(ctx, error):
    embed.title="Info"
    if isinstance(error, commands.BadArgument):
        embed.description = "User not found"
    
    elif isinstance(error, commands.CommandError):
        embed.description = "Command Example:\n>info <@{0.id}>".format(ctx.author)

    await ctx.send(embed=embed)


@commands.guild_only()
@bot.command(pass_context=True)
async def avatar(ctx, member: discord.Member=None):
    await ctx.send(member.avatar_url)


@avatar.error
async def avatar_error(ctx, error):
    embed.title="Avatar"
    if isinstance(error, commands.BadArgument):
        embed.description = "User not found"

    elif isinstance(error, commands.CommandError):
        embed.description = "Command Example:\n>avatar <@{0.id}>".format(ctx.author)

    await ctx.send(embed=embed)


@commands.guild_only()
@bot.command(pass_context=True)
async def dm(ctx, member: discord.Member=None, *message):
    await member.send(' '.join(message))
    await ctx.message.delete()


@dm.error
async def dm_error(ctx, error):
    embed.title="dm"
    if isinstance(error, commands.BadArgument):
        embed.description = "User not found"
    
    elif isinstance(error, commands.CommandError):
        embed.description = "Command Example:\n>dm <@{0.id}> wats up dude".format(ctx.author)
    
    await ctx.send(embed=embed)


@commands.guild_only()
@bot.command(pass_context=True)
async def sanic(ctx, *, text=None):
	img = await helpers.create_sanic_image(text)
	img.seek(0)
	await ctx.send(file=discord.File(img, "sanic.jpg"))


for extension in extensions:
    bot.load_extension(extension)

bot.run(os.environ["UNRBOTKEY"])
