import consts
import discord
from discord.ext import commands
import helpers


class GamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ttt_board = [['.','.','.'],['.','.','.'],['.','.','.']]
        self.ttt_cache = dict()

    # Tic Tac Toe against the one and only TicTacToe grandmaster
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def ttt(self, ctx, x: int = -1, y: int = -1):
        embed = discord.Embed(color=consts.color)
        embed.set_thumbnail(url=consts.avatar)
        try:
            author_id = ctx.author.id
            if author_id not in self.ttt_cache.keys(): 
                self.ttt_cache[author_id] = [self.ttt_board,0,False]
                msg = "It's your turn <@{0}>!\n>ttt row col | make a move\n\n".format(author_id)
                msg += await helpers.convert_board(self.ttt_board)
                await ctx.send(msg)
                return
            elif author_id in self.ttt_cache.keys():
                state = self.ttt_cache[author_id]
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
                            self.ttt_cache.pop(author_id,None)
                            await ctx.send(msg)
                            return
                        elif await helpers.check_draw(state[0]):
                            msg = "You're a good player... GG! :)\n\n"
                            msg += await helpers.convert_board(state[0])
                            self.ttt_cache.pop(author_id,None)   
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
                            self.ttt_cache.pop(author_id,None)
                            await ctx.send(msg)
                            return
                        elif await helpers.check_draw(state[0]):
                            msg = "You're a good player... GG! :)\n\n"
                            msg += await helpers.convert_board(state[0])
                            self.ttt_cache.pop(author_id,None)   
                            await ctx.send(msg)
                            return
                        msg = "It's your turn <@{0}>!\n\n".format(author_id)
                        msg += await helpers.convert_board(state[0])
                        await ctx.send(msg)
                elif x == -1 and y == -1:
                    board = self.ttt_cache[author_id]
                    msg = "It's your turn!\n\n"
                    msg += await helpers.convert_board(state[0])
                    await ctx.send(msg)
        except:
            embed.title = "TicTacToe"
            embed.description = "Usage: \n>ttt | start a game\n>ttt x y | make a move"
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(GamesCog(bot))
