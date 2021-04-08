import discord
from discord.ext import commands
import os
import random


class PicturesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.image_cache = dict()

    @commands.guild_only()
    @commands.command(pass_context=True)
    async def cheese(self, ctx):
        path = os.getcwd() + "/images/cheese/"
        filename = random.choice(os.listdir(path))
        full_path = path+filename

        try:
            if filename not in self.image_cache.keys():
                image = open(full_path, "rb")
                await ctx.send(file=discord.File(image, "cheese.png"))
                self.image_cache[filename] = image
                self.image_cache[filename].seek(0)
            else:
                print("Using cached pointer:   " + filename)
                await ctx.send(file=discord.File(self.image_cache[filename], "cheese.png"))
                self.image_cache[filename].seek(0)
        except:
            return
       

    @commands.guild_only()
    @commands.command(pass_context=True)
    async def ham(self, ctx):
        path = os.getcwd() + "/images/ham/"
        filename = random.choice(os.listdir(path))
        full_path = path+filename

        try:
            if filename not in self.image_cache.keys():
                image = open(full_path, "rb")
                await ctx.send(file=discord.File(image, "ham.png"))
                self.image_cache[filename] = image
                self.image_cache[filename].seek(0)
            else:
                print("Using cached pointer:   " + filename)
                await ctx.send(file=discord.File(self.image_cache[filename], "ham.png"))
                self.image_cache[filename].seek(0)
        except:
            return


    # sends a sam hyde meme
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def samhyde(self, ctx):
        path = os.getcwd() + "/images/samhyde/"
        filename = random.choice(os.listdir(path))
        full_path = path+filename
        print(full_path)

        try:
            if filename not in self.image_cache.keys():
                image = open(full_path, "rb")
                await ctx.send(file=discord.File(image, "samhyde.png"))
                self.image_cache[filename] = image
                self.image_cache.seek(0)
            else:
                print("Using cached pointer:   " + filename)
                await ctx.send(file=discord.File(self.image_cache[filename], "samhyde.png"))
                self.image_cache[filename].seek(0)
        except:
            return

def setup(bot):
    bot.add_cog(PicturesCog(bot))
