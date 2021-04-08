import consts
from datetime import datetime
from datetime import timedelta
import discord
from discord.ext import commands


class UtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Changes the role of the user
    # Definitely needs organizational/functional changes
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def role(self, ctx, role=None):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title="Role"
        if not role:
            embed.description = text.role_description
            await ctx.send(embed=embed)
            return

        d_get = discord.utils.get
        g_roles = ctx.guild.roles
        
        member = ctx.message.author
        member_roles = [role.name for role in member.roles]

        selected_role=None
        role = role.lower() # make input case insensitive
        all_year_roles = ["Freshman", "Sophomore", "Junior", "Senior", "5th+ Year", "Masters Student", "Doc Student", "Alumnus"]
        original_len = len(all_year_roles)

        # Undergraduate students
        freshman = ["freshman","freshmen","fresh"]
        sophomore = ["sophomore", "soph"]
        junior, senior, fifth_year_plus = "junior", "senior", "5th+"
     
        # Graduate students
        doc_student, masters_student = "phd", "masters"
        alumnus = ["alumnus", "alumni"]

        # Fun roles
        all_fun_roles = ["Gamer"]
        fun_bool = False

        year_campus_toggle = True # True means we are changing year role, False means mode (online, on-campus)

        fetch = consts.roles_dict[role]

        if fetch in member_roles:
            role_to_remove = d_get(g_roles, name=fetch)
            await member.remove_roles(role_to_remove)
            await ctx.send("Role **{0}** removed! <@{1}> ".format(fetch, member.id))
            return
        
        if fetch in all_year_roles:
            selected_role = d_get(g_roles, name=fetch)
            all_year_roles.remove(fetch)

        all_year_roles = tuple(all_year_roles)
        remove_roles = tuple(d_get(g_roles, name=n) for n in all_year_roles)

        if fetch in all_fun_roles:
            selected_role = d_get(g_roles, name=fetch)
            fun_bool = True 

        await member.add_roles(selected_role)
        if not fun_bool:
            await member.remove_roles(*remove_roles)

        await ctx.send("Role **{0}** added! <@{1}>".format(fetch, member.id))


    @commands.guild_only()
    @commands.command(pass_context=True)
    async def info(self, ctx, member: discord.Member=None):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.title = "Info"
        joined = member.joined_at.replace(microsecond=0) - timedelta(hours=8)
        embed.description = "<@{0.id}> ".format(member) + "joined on `{0}`".format(joined) + " and has been a member of this server for `{0}`".format(datetime.now().replace(microsecond=0)-joined)
        await ctx.send(embed=embed) 


    @info.error
    async def info_error(self, ctx, error):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        embed.title="Info"
        if isinstance(error, commands.BadArgument):
            embed.description = "User not found"
        
        elif isinstance(error, commands.CommandError):
            embed.description = "Command Example:\n>info <@{0.id}>".format(ctx.author)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UtilsCog(bot))

