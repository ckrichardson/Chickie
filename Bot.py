import asyncio
from bs4 import BeautifulSoup
from copy import deepcopy
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
import smtplib
import text
import time
import wikipedia


#Intents (this is necessary for the welcome message)
intents = discord.Intents.all()

# Prefix used for the bot
prefix = '>'
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Declare the embed characteristics here
color = 0
avatar = ""
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
	global color
	global avatar
	global embed

	color = 0xC0C0C0
	avatar = "https://cdn.discordapp.com/avatars/755173405602480289/5c43363260893ef6d6f6de37193b7057.png?size=256"
	embed = discord.Embed(color=color)
	embed.set_thumbnail(url=avatar)

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


# Changes the role of the user
# Definitely needs organizational/functional changes
@commands.guild_only()
@bot.command(pass_context=True)
async def role(ctx, role=None):
    embed.title="Role"
    if not role:
        embed.description = text.role_description
        await ctx.send(embed=embed)
        return

    d_get = discord.utils.get
    g_roles = ctx.guild.roles
    
    member = ctx.message.author

    selected_role=None
    role = role.lower() # make input case insensitive
    all_year_roles = ["Freshman", "Sophomore", "Junior", "Senior", "5th+ Year", "Masters Student", "Doc Student", "Alumnus"]
    all_modes = ["On-Campus Student", "Online Student"]
    original_len = len(all_year_roles)

    # Undergraduate students
    freshman = ["freshman","freshmen","fresh"]
    sophomore = ["sophomore", "soph"]
    junior, senior, fifth_year_plus = "junior", "senior", "5th+"
 
    # Graduate students
    doc_student, masters_student = "phd", "masters"
    alumnus = ["alumnus", "alumni"]
    on_campus_off_campus = ["online","on-campus"]

    # Fun roles
    fun_roles = ["gamer"]
    fun_bool = False

    year_campus_toggle = True # True means we are changing year role, False means mode (online, on-campus)

    # Year Roles 
    if role in freshman:
        selected_role = d_get(g_roles, name="Freshman")
        all_year_roles.remove("Freshman")
    elif role in sophomore:
        selected_role = d_get(g_roles, name="Sophomore")
        all_year_roles.remove("Sophomore")
    elif role == junior:
        selected_role = d_get(g_roles, name="Junior")
        all_year_roles.remove("Junior")
    elif role == senior:
        selected_role = d_get(g_roles, name="Senior")
        all_year_roles.remove("Senior")
    elif role == fifth_year_plus:
        selected_role = d_gete(g_roles, name="5th+ Year")
        all_year_roles.remove("5th+ Year")
    elif role == masters_student:
        selected_role = d_get(g_roles, name="Masters Student")
        all_year_roles.remove("Masters Student")
    elif role == doc_student: 
        selected_role = d_get(g_roles, name="Doc Student")
        all_year_roles.remove("Doc Student")
    elif role in alumnus:
        selected_role = d_get(g_roles, name="Alumnus")
        all_year_roles.remove("Alumnus")
        remove_campus_roles = tuple(d_get(g_roles, name=n) for n in all_modes)
        await member.remove_roles(*remove_campus_roles)

    all_year_roles = tuple(all_year_roles)

    # Online / On-Campus Roles
    # Remove all other roles (year-related, or online/on-campus) apart from the one we are adding (cannot be freshman AND sophomore, Junior AND senior, etc.)
    if not len(all_year_roles) - original_len:
        year_campus_toggle = False
        if role==on_campus_off_campus[0]:
            selected_role = d_get(g_roles, name="Online Student")
            on_campus_off_campus = tuple(["On-Campus Student"])
        elif role==on_campus_off_campus[1]:
            selected_role = d_get(g_roles, name="On-Campus Student")
            on_campus_off_campus = tuple(["Online Student"])

        remove_roles = tuple(d_get(g_roles, name=n) for n in on_campus_off_campus) 
    else: 
        remove_roles = tuple(d_get(g_roles, name=n) for n in all_year_roles)

    if role in fun_roles:
        selected_role = d_get(g_roles, name=role.title())
        fun_bool = True 

    await member.add_roles(selected_role)
    if not fun_bool:
        await member.remove_roles(*remove_roles)


# Kicks a user from the server
@commands.guild_only()
@commands.has_permissions(kick_members=True)
@bot.command(pass_context=True)
async def kick(ctx, member: discord.Member=None, *, reason=None):
    embed.title="Kick"
    if ctx.author == member:
        embed.description = "You tryin' to kick yourself brah?"
        await ctx.send(embed=embed)
        return

    for role in member.roles:
        if role.name == "Owner" or role.name == "Mod":
            embed.description = "Sorry!   This person cannot be kicked."
            await ctx.send(embed=embed)
            return

    if not member:
        return

    else:
        embed.description = "<@{0}>".format(member.id) + " just got nae-nae'd!!!"
        await ctx.send(embed=embed)
        embed.title = "KICKED"
        embed.description = ("You have been kicked from the \"UNR Community\" server for the following reason:\n\n" + reason)
        embed.timestamp = datetime.today() + timedelta(hours=7)
        await member.send(embed=embed)
        await member.kick(reason=reason)


@kick.error
async def kick_error(ctx, error):
    embed.title="Kick"
    if isinstance(error, commands.MissingPermissions):
        embed.description = "<@{0}>".format(ctx.author.id) + " you do not have the permissions to run this command"
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandError):
        embed.description = "Command example:\n>kick <@{0}> reason".format(ctx.author.id)    
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed.description = "I cannot find this member"
        await ctx.send(embed=embed)
    

# Bans a user from the server
@commands.guild_only()
@commands.has_permissions(ban_members=True)
@bot.command(pass_context=True)
async def ban(ctx, member: discord.Member=None, *, reason=None):

    embed.title = "Ban"
    if ctx.author == member:
        embed.description = "You tryin' to ban yourself brah?"
        await ctx.send(embed=embed)
        return

    for role in member.roles:
        if role.name == "Owner" or role.name == "Mod":
            embed.description = "Sorry!   This person cannot be banned."
            await ctx.send(embed=embed)
            return

    if not member:
        return

    else:
        await member.ban(reason=reason)
        embed.description = "<@{0}>".format(member.id) + "  JUST GOT FKING BAN HAMMERED!!!\n\nReason: {0}".format(reason)
        await ctx.send(embed=embed)
        embed.title = "BANNED"
        embed.description = ("You have been banned from the \"UNR Community\" server for the following reason:\n\n"
                             + reason)
        embed.timestamp = datetime.today() + timedelta(hours=7)
        await member.send(embed=embed)


@ban.error
async def ban_error(ctx, error):
    embed.title="Ban"
    if isinstance(error, commands.MissingPermissions):
        embed.description = "<@{0}>".format(ctx.author.id) + " you do not have the permissions to banhammer."
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandError):
        embed.description = "Command example:\n>ban <@{0}> reason".format(ctx.author.id)    
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed.description = "I cannot find this member"
        await ctx.send(embed=embed)


# Mutes a user
@commands.guild_only()
@commands.has_permissions(kick_members=True)
@bot.command(pass_context=True)
async def mute(ctx, user: discord.Member=None, duration: int=0, *, reason=None):
    embed.title = "Mute"
    embed.description = "<@{0}>".format(user.id) + " has been muted for " + str(duration) + " minutes for:\n\n" + reason

    roles = [role.name for role in user.roles if role.name != "@everyone"]
    
    remove_roles = tuple(discord.utils.get(ctx.guild.roles, name=n) for n in roles)
    muted = discord.utils.get(ctx.guild.roles, name="Muted")

    await user.add_roles(muted)
    await user.remove_roles(*remove_roles)
    await ctx.send(embed=embed)

    await asyncio.sleep(duration * 60)

    await user.add_roles(*remove_roles)
    await user.remove_roles(muted)


@mute.error
async def mute_error(ctx, error):
    embed.title="Mute"
    if isinstance(error, commands.MissingPermissions):
        embed.description = "<@{0}>".format(ctx.author.id) + " you do not have the permissions to mute."
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandError):
        embed.description = "Command example:\n>mute <@{0}> 1 reason\n\n*Note: length of mute is in minutes*".format(ctx.author.id)    
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed.description = "I cannot find this member"
        await ctx.send(embed=embed)


# Deletes the last 'x' number of messages
@commands.guild_only()
@commands.has_any_role("Mod","Owner")
@bot.command(pass_context=True)
async def purge(ctx, number: int=0):
    # Error handler cannot catch purge number of 0 (number+1), this must be handled here
    if not number:
        embed.title = "Purge"
        embed.description = "Command Example: " + prefix + "purge 10"
        await ctx.send(embed=embed)
        return
    if number > 100:
        embed.description="100-line limit per purge."
        await ctx.send(embed=embed)
        return
    try:
        await ctx.channel.purge(limit=(number+1))
    except:
        return


# sends a sam hyde meme
@commands.guild_only()
@bot.command(pass_context=True)
async def samhyde(ctx):
    path = os.getcwd() + "/images/samhyde/"
    filename = random.choice(os.listdir(path))
    full_path = path+filename
    print(full_path)

    try:
        if filename not in global_image_pointer_cache.keys():
            image = open(full_path, "rb")
            await ctx.send(file=discord.File(image, "samhyde.png"))
            global_image_pointer_cache[filename] = image
            global_image_pointer_cache[filename].seek(0)
        else:
            print("Using cached pointer:   " + filename)
            await ctx.send(file=discord.File(global_image_pointer_cache[filename], "samhyde.png"))
            global_image_pointer_cache[filename].seek(0)
    except:
        return


# Get the weather of a location
@commands.guild_only()
@bot.command()
async def weather(ctx, *location):
    global color
    valid_weather = {"Clear": ":sunny:", "Clouds": ":cloud:", \
                     "Rain": ":cloud_rain:", "Snow": ":snowflake:"}

    owm = pyowm.OWM(owm_api_key)

    if not len(location):
        location = "Reno"
    else:
        location = ' '.join(word for word in location)
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    fc = owm.three_hours_forecast(location)
    f = fc.get_forecast()
    temps = w.get_temperature("fahrenheit")
    humidity = w.get_humidity()    
    current_temp = temps["temp"]
    temp_max = temps["temp_max"]
    temp_min = temps["temp_min"]
    forecasts = ""
    first_weather_status = None
    weather_icon = None
    start_time = None

    for weather in f:
        time = weather.get_reference_time("date")
        if not start_time:
            start_time = time
            first_weather_status = weather.get_status()
            if first_weather_status in valid_weather:
                weather_icon = weather.get_weather_icon_url()
        if time - timedelta(hours=24) > start_time:
            break
        pst = time - timedelta(hours=7)
        forecasts += "`" + pst.strftime("%m/%d .... %H:%M") + "` "
        forecasts += valid_weather[weather.get_status()] + "\n"

    current_max_min = "Now:   " + str(current_temp) + "   \nMax:   " + str(temp_max) + "   \nMin:   " + str(temp_min)
    conditions = "Skies:   " + first_weather_status + "\nHumidity:   " + str(humidity) + "%"
   
    embed = discord.Embed()
    embed.title="Weather in " + location.lower().title()
    embed.set_thumbnail(url=weather_icon)
    embed.add_field(name="Temperature", value=current_max_min)
    embed.add_field(name="Conditions", value=conditions, inline=True)
    embed.add_field(name="24 Hour Forecast (PST)", value=forecasts)
    await ctx.send(embed=embed)


@weather.error
async def weather_error(ctx, error):
	embed.title = "Weather"
	if isinstance(error, commands.CommandInvokeError):
		embed.description = "Couldn't find that location"

	await ctx.send(embed=embed)


# Retrieve AQI of reno
@commands.guild_only()
@bot.command(pass_context=True)
async def aqi(ctx):
    embed.title = "AQI Reno Area"
    embed.description = await helpers.get_aqi()
    await ctx.send(embed=embed)


# Search wikipedia for something and return the first 3 sentences, and maybe an image
@commands.guild_only()
@bot.command(pass_context=True)
async def wiki(ctx, *search):
    query = ' '.join(search)
    global color

    if query=="":
        embed = discord.Embed()
        embed.description="Usage:   "+prefix+"wiki put_query_here"
        embed.title = "Wiki"
        await ctx.send(embed=embed)
        return 

    try:
        resolved_page = wikipedia.page(query)
        url = resolved_page.url
        summary = wikipedia.summary(query, sentences=3)

        preferred_image_url = None
        title = resolved_page.title
        refined_title = title.replace(" ", "_")

        for image in resolved_page.images:
            if refined_title.lower() in image.lower() and ("jpg" in image or "png" in image):
                preferred_image_url = image

        if not preferred_image_url:
            try:
                if len(resolved_page.images):
                    preferred_image_url = resolved_page.images[2]
                else:
                    None
            except:
                None

        if len(url + "\n\n" + summary) > 2048:
            statement = (url + "\n\n" + summary)[2045:] + "..."
        else:
            statement = url + "\n\n" + summary
        embed_a = discord.Embed(title=title,description=statement)
        if preferred_image_url and preferred_image_url:
            embed_a = embed_a.set_thumbnail(url=preferred_image_url)

    except wikipedia.exceptions.DisambiguationError as e:
        list_of_options = "Did you mean one of these...?\n\n"
        counter = 1
        limit = 20

        if len(e.options) < 20:
            limit = len(e.options)

        for i in range(limit):
            list_of_options = list_of_options + str(counter) + ".   " + e.options[i] + "\n"
            counter += 1

        embed = discord.Embed(title="Oops!", description=list_of_options, color=color)

    except wikipedia.exceptions.PageError as e:
        embed_a = discord.Embed(title="Oops!", description="Couldn't find what you were looking for!", color=color)

    await ctx.send(embed=embed_a)


# Get covid stats from the coronavirus dashboard of UNR
@commands.guild_only()
@bot.command(pass_context=True)
async def covid(ctx):
    global color
    avatar = "https://timesofindia.indiatimes.com/thumb/msid-73928661,width-1200,height-900,resizemode-4/.jpg"
    data = await helpers.get_covid_data()
    active = "`{0}`".format(data[0])
    recovered = "`{0}`".format(data[1])
    total = "`{0}`".format(data[2])
    update = "{0}".format(data[3])

    embed = discord.Embed(color=color)
    embed.set_thumbnail(url=avatar)
    embed.title = "UNR Covid Cases"
    embed.add_field(name="Active", value=active)
    embed.add_field(name="Recovered", value=recovered, inline=True)
    embed.add_field(name="Total", value=total, inline=True)
    embed.set_footer(text=update)
    await ctx.send(embed=embed)


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


# Say hello to the bot
@commands.guild_only()
@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.trigger_typing()
    await asyncio.sleep(1)
    await ctx.send("Hi <@{0}> :baby_chick:".format(ctx.author.id))


# Tic Tac Toe against the one and only TicTacToe grandmaster
@commands.guild_only()
@bot.command(pass_context=True)
async def ttt(ctx, x: int = -1, y: int = -1):
    try:
        global ttt_cache
        author_id = ctx.author.id
        if author_id not in ttt_cache.keys(): 
            blank_board = [['.','.','.'],['.','.','.'],['.','.','.']]
            ttt_cache[author_id] = [blank_board,0,False]
            msg = "It's your turn <@{0}>!\n>ttt row col | make a move\n\n".format(author_id)
            msg += await helpers.convert_board(blank_board)
            await ctx.send(msg)
            return
        elif author_id in ttt_cache.keys():
            state = ttt_cache[author_id]
            if state[2]:
                msg = "It's not your turn yet!"
                await ctx.send(msg)
                return
            if x >= 1 and x <= 3 and y >= 1 and y <= 3:
                if state[0][x-1][y-1] != '.':
                    pass
                else:
                    state[0][x-1][y-1] = "O"
                    state[1] += 1
                    state[2] = not state[2]
                    if await helpers.check_victory(state[0]):
                        msg =  "You have bested me. Well played! DM <@{0}> for a reward!\n\n".format("247261235228311552")
                        msg += await helpers.convert_board(state[0])
                        ttt_cache.pop(author_id,None)
                        await ctx.send(msg)
                        return
                    elif await helpers.check_draw(state[0]):
                        msg = "You're a good player... GG! :)\n\n"
                        msg += await helpers.convert_board(state[0])
                        ttt_cache.pop(author_id,None)   
                        await ctx.send(msg)
                        return
                    msg = "Good move! Thinking..."
                    await ctx.send(msg)
                    r = await helpers.minmax(state[0],state[1],state[2])
                    state[0][r[1]][r[2]] = "X"
                    state[1] += 1
                    state[2] = not state[2]
                    if await helpers.check_victory(state[0]):
                        msg =  "You got pwned... but well played!\n\n"
                        msg += await helpers.convert_board(state[0])
                        ttt_cache.pop(author_id,None)
                        await ctx.send(msg)
                        return
                    elif await helpers.check_draw(state[0]):
                        msg = "You're a good player... GG! :)\n\n"
                        msg += await helpers.convert_board(state[0])
                        ttt_cache.pop(author_id,None)   
                        await ctx.send(msg)
                        return
                    msg = "It's your turn <@{0}>!\n\n".format(author_id)
                    msg += await helpers.convert_board(state[0])
                    await ctx.send(msg)
            elif x == -1 and y == -1:
                board = ttt_cache[author_id]
                msg = "It's your turn!\n\n"
                msg += await helpers.convert_board(state[0])
                await ctx.send(msg)
    except:
        embed.title = "TicTacToe"
        embed.description = "Usage: \n>ttt | start a game\n>ttt x y | make a move"
        await ctx.send(embed=embed)


# Hangman
@commands.guild_only()
@bot.command(pass_context=True)
async def hm(ctx, letter=None):
    global words
    global hangman_states
    author_id = ctx.author.id
    if author_id not in hangman_cache.keys(): 
        if not words: 
            path = os.getcwd() + "/words.txt"
            with open(path, "r") as word_file:
                words = [line for line in word_file]
        selected_word = random.choice(words).upper().strip()
        stage = 0
        missed = list()
        guessed = [0 for x in range(len(selected_word))]
        hangman_cache[author_id] = [stage, list(selected_word), guessed, missed]
        msg = "Take a guess <@{0}>!\nGuess with:   >hm (letter)".format(author_id)
        blanks = "\n\n"
        for i in range(len(selected_word)):
            if guessed[i]:
                blanks += selected_word[i]+" "
            else:
                blanks += "_ "
        await ctx.send(msg)
        await ctx.send(hangman_states[stage]+blanks+"\nMissed:   "+ " ".join(missed)+"```")

    elif author_id in hangman_cache.keys() and letter:
        if letter == "quit":
            hangman_cache.pop(author_id, None)
            await ctx.send("Successfully quit!")
            return
        letter = list(letter)[0].upper()
        blanks = ""
        missed = hangman_cache[author_id][3]
        guessed = hangman_cache[author_id][2]
        selected_word = hangman_cache[author_id][1]
        stage = hangman_cache[author_id][0]
        found = False

        for i in range(len(selected_word)):
            if guessed[i]:
                blanks += selected_word[i]+" "
            else:
                blanks += "_ "

        if letter in missed or letter in blanks:
            await ctx.send("You've already guessed that letter!")
            await ctx.send(hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")
            return

        elif stage < 7:
            blanks = "\n\n"
            for i in range(len(selected_word)):
                if selected_word[i] == letter:
                    guessed[i] = True
                    found = True
            if not found:
                missed.append(letter)
                hangman_cache[author_id][0] += 1
                stage += 1
                
            for i in range(len(selected_word)):
                if guessed[i]:
                    blanks += selected_word[i]+" "
                else:
                    blanks += "_ "

            if 0 not in guessed:
                blanks = "\n\n" + ' '.join(selected_word)
                await ctx.send("Hurrah for <@{0}>, you've saved the day!".format(author_id))
                await ctx.send(hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")
                hangman_cache.pop(author_id, None)
                return   

            if hangman_cache[author_id][0] == 7:
                blanks = "\n\n" + ' '.join(x for x in selected_word)
                await ctx.send("You've let him hang <@{0}>, how could you...".format(author_id))
                await ctx.send(hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")
                hangman_cache.pop(author_id, None)
                return
    
        await ctx.send("Take another guess <@{0}>!".format(author_id)) 
        await ctx.send(hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")


    elif author_id in hangman_cache.keys() and not letter:
        embed.title = "Hangman"
        embed.description = "Usage:   >hangman (letter)"
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


@commands.guild_only()
@bot.command(pass_context=True)
async def cheese(ctx):
    path = os.getcwd() + "/images/cheese/"
    filename = random.choice(os.listdir(path))
    full_path = path+filename

    try:
        if filename not in global_image_pointer_cache.keys():
            image = open(full_path, "rb")
            await ctx.send(file=discord.File(image, "cheese.png"))
            global_image_pointer_cache[filename] = image
            global_image_pointer_cache[filename].seek(0)
        else:
            print("Using cached pointer:   " + filename)
            await ctx.send(file=discord.File(global_image_pointer_cache[filename], "cheese.png"))
            global_image_pointer_cache[filename].seek(0)
    except:
        return
   

@commands.guild_only()
@bot.command(pass_context=True)
async def ham(ctx):
    path = os.getcwd() + "/images/ham/"
    filename = random.choice(os.listdir(path))
    full_path = path+filename

    try:
        if filename not in global_image_pointer_cache.keys():
            image = open(full_path, "rb")
            await ctx.send(file=discord.File(image, "ham.png"))
            global_image_pointer_cache[filename] = image
            global_image_pointer_cache[filename].seek(0)
        else:
            print("Using cached pointer:   " + filename)
            await ctx.send(file=discord.File(global_image_pointer_cache[filename], "ham.png"))
            global_image_pointer_cache[filename].seek(0)
    except:
        return


bot.run(os.environ["UNRBOTKEY"])
