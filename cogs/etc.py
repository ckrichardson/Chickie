import asyncio
import consts
import discord
from discord.ext import commands
import helpers
import random


class EtcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes = None

    # Say hello to the bot
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def hello(self, ctx):
        await ctx.trigger_typing()
        await asyncio.sleep(1)
        await ctx.send("Hi <@{0}> :baby_chick:".format(ctx.author.id))



    # Sends you a motivational quote
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def quote(self, ctx):
        if not self.quotes:
            self.quotes = await helpers.get_quotes()
        selected_quote = dict(random.choice(self.quotes))
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title = "Quote"
        embed.description = "\"{0}\"\n-{1}".format(selected_quote["text"], selected_quote["author"])
        await ctx.send(embed=embed)


    # Find out your pp size
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def pp(self, ctx):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        author_id = ctx.author.id
        sizes = {0: "micropenis", 1: "smol pp", 2: "regular pp", 3: "respectable pp", 4: "gargantuan pp", 5: "Chad McThundercock"}
        embed.title = "PP"
        embed.description = "<@{0}> has a `{1}`".format(author_id, sizes[[author_id % 5,5][author_id==131591965551624193]])

        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.command(pass_context=True)
    async def insult(self, ctx, target: discord.Member=None):
        insult = await helpers.get_insult()
        if not target:
            msg = "<@{0}> ".format(ctx.author.id) + insult
        else:
            msg = "<@{0}> ".format(target.id) + insult
        await ctx.send(msg)


    @insult.error
    async def insult_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title="Insult"
        if isinstance(error, commands.BadArgument):
            embed.description = "User not found"
        
        elif isinstance(error, commands.CommandError):
            embed.description = "Command Example:\n>insult <@{0.id}>".format(ctx.author)

        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.command(pass_context=True)
    async def sanic(self, ctx, *, text=None):
            img = await helpers.create_sanic_image(text)
            img.seek(0)
            await ctx.send(file=discord.File(img, "sanic.jpg"))


    @commands.guild_only()
    @commands.command(pass_context=True)
    async def dm(self, ctx, member: discord.Member, *message):
        await member.send(' '.join(message))
        await ctx.message.delete()


    @dm.error
    async def dm_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title="dm"
        if isinstance(error, commands.BadArgument):
            embed.description = "User not found"
        
        elif isinstance(error, commands.CommandError):
            embed.description = "Command Example:\n>dm <@{0.id}> wats up dude".format(ctx.author)
    


def setup(bot):
    bot.add_cog(EtcCog(bot))
