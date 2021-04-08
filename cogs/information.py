import consts
from datetime import timedelta
import discord
from discord.ext import commands
import helpers
import os
import pyowm
import wikipedia


class InformationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owm_api_key = os.environ["OWMAPIKEY"]

    # Get the weather of a location
    @commands.guild_only()
    @commands.command()
    async def weather(self, ctx, *location):
        valid_weather = {"Clear": ":sunny:", "Clouds": ":cloud:", \
                         "Rain": ":cloud_rain:", "Snow": ":snowflake:"}

        owm = pyowm.OWM(self.owm_api_key)

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
       
        embed = discord.Embed(color=consts.color)
        embed.title="Weather in " + location.lower().title()
        embed.set_thumbnail(url=weather_icon)
        embed.add_field(name="Temperature", value=current_max_min)
        embed.add_field(name="Conditions", value=conditions, inline=True)
        embed.add_field(name="24 Hour Forecast (PST)", value=forecasts)
        await ctx.send(embed=embed)


    @weather.error
    async def weather_error(self, ctx, error):
            embed = discord.Embed(color=consts.color)
            embed.title = "Weather"
            if isinstance(error, commands.CommandInvokeError):
                    embed.description = "Couldn't find that location"

            await ctx.send(embed=embed)


    # Retrieve AQI of reno
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def aqi(self, ctx):
        embed = discord.Embed(color=consts.color)
        embed.title = "AQI Reno Area"
        embed.description = await helpers.get_aqi()
        await ctx.send(embed=embed)


    # Search wikipedia for something and return the first 3 sentences, and maybe an image
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def wiki(self, ctx, *search):
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
    @commands.command(pass_context=True)
    async def covid(self, ctx): 
        embed = discord.Embed(color=consts.color)
        covid_avatar = "https://timesofindia.indiatimes.com/thumb/msid-73928661,width-1200,height-900,resizemode-4/.jpg"
        embed.set_thumbnail(url=covid_avatar)
        embed.title = "UNR Covid Cases"
        data = await helpers.get_covid_data()
        active = "`{0}`".format(data[0])
        recovered = "`{0}`".format(data[1])
        total = "`{0}`".format(data[2])
        update = "{0}".format(data[3])

        embed.add_field(name="Active", value=active)
        embed.add_field(name="Recovered", value=recovered, inline=True)
        embed.add_field(name="Total", value=total, inline=True)
        embed.set_footer(text=update)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(InformationCog(bot))
