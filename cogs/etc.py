import asyncio
import discord
from discord.ext import commands


class EtcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Say hello to the bot
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def hello(self, ctx):
        await ctx.trigger_typing()
        await asyncio.sleep(1)
        await ctx.send("Hi <@{0}> :baby_chick:".format(ctx.author.id))


def setup(bot):
    bot.add_cog(EtcCog(bot))
