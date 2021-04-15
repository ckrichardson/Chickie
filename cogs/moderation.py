import asyncio
import consts
from datetime import datetime
from datetime import timedelta
import discord
from discord.ext import commands


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Kicks a user from the server
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True)
    async def kick(self, ctx, member: discord.Member=None, *, reason=None):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
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
            embed.description = "<@{0}>".format(member.id) + " just got nae-nae'd!!!\n\n" + "Reason: " + reason
            await ctx.send(embed=embed)
            embed.title = "KICKED"
            embed.description = ("You have been kicked from the \"UNR Community\" server for the following reason:\n\n" + reason)
            embed.timestamp = datetime.today() + timedelta(hours=7)

            #this try statement is in case the kicked  user cannot be DM'd
            try:
                await member.send(embed=embed)
            except:
                pass

            await member.kick(reason=reason)


    @kick.error
    async def kick_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
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
    @commands.command(pass_context=True)
    async def ban(self, ctx, member: discord.Member=None, *, reason=None):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)

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

        if not reason: 
            embed.description = "Command example:\n>ban <@{0}> reason".format(ctx.author.id)    
            await ctx.send(embed=embed)

        else:
            embed.description = "<@{0}>".format(member.id) + "  JUST GOT FKING BAN HAMMERED!!!\n\nReason: {0}".format(reason)
            await ctx.send(embed=embed)
            embed.title = "BANNED"
            embed.description = ("You have been banned from the \"UNR Community\" server for the following reason:\n\n"
                                 + reason)
            embed.timestamp = datetime.today() + timedelta(hours=7)

            #This try statement is for if the user cannot be DM'd
            try:
                await member.send(embed=embed)
            except:
                pass

            await member.ban(reason=reason)

    @ban.error
    async def ban_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
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
    @commands.command(pass_context=True)
    async def mute(self, ctx, user: discord.Member=None, duration: int=0, *, reason=None):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title = "Mute"
        embed.description = "<@{0}>".format(user.id) + " has been muted for " + str(duration) + " minutes for:\n\n" + reason

        roles = [role.name for role in user.roles if role.name != "@everyone"]
        
        if len(roles):
            remove_roles = tuple(discord.utils.get(ctx.guild.roles, name=n) for n in roles)
        muted = discord.utils.get(ctx.guild.roles, name="Muted")

        await user.add_roles(muted)
        if len(roles):
            await user.remove_roles(*remove_roles)
        await ctx.send(embed=embed)

        await asyncio.sleep(duration * 60)

        if len(roles):
            await user.add_roles(*remove_roles)
        await user.remove_roles(muted)


    @mute.error
    async def mute_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
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
    @commands.command(pass_context=True)
    async def purge(self, ctx, number: int=0):
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



    # Changes the status of the bot
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(pass_context=True)
    async def status(self, ctx,*,game=None):
        game = discord.Game(str(game))
        await self.bot.change_presence(activity=game)



    @status.error
    async def status_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title="Status"
        if isinstance(error, commands.MissingPermissions):
            embed.description="You do not have the permissions to use this command"

        elif isinstance(error, commannds.CommandError):
            embed.description="Command example:\n>status looking for booty"

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ModerationCog(bot))
