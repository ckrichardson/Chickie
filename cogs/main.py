import discord
from discord.ext import commands
import text


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Things to run once the bot successfully authenticates
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online")
        game = discord.Game("Fluffing Feathers")
        await self.bot.change_presence(activity=game)


    # Things to run when a member joins the server
    # Currently sends them a welcome message
    @commands.Cog.listener()
    async def on_member_join(self, member):
            embed.title = "Welcome!"
            embed.description = text.rules
            await member.send(embed=embed)


def setup(bot):
    bot.add_cog(MainCog(bot))
