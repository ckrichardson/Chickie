import consts
from datetime import timedelta
import discord
from discord.ext import commands
import os
import pyowm


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


def setup(bot):
    bot.add_cog(InformationCog(bot))
