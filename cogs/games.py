import consts
import discord
from discord.ext import commands
import helpers
import os
import random
from random import randrange

class GamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ttt_board = [['.','.','.'],['.','.','.'],['.','.','.']]
        self.ttt_cache = dict()
        self.hangman_cache = dict()
        self.hangman_states = None
        self.words = list()

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


    # Hangman
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def hm(self, ctx, letter=None):
        if not self.hangman_states:
            self.hangman_states = await helpers.get_hm_states()

        author_id = ctx.author.id
        if author_id not in self.hangman_cache.keys(): 
            if not self.words: 
                path = os.getcwd() + "/resources/words.txt"
                with open(path, "r") as word_file:
                    words = [line for line in word_file]
            selected_word = random.choice(words).upper().strip()
            stage = 0
            missed = list()
            guessed = [0 for x in range(len(selected_word))]
            self.hangman_cache[author_id] = [stage, list(selected_word), guessed, missed]
            msg = "Take a guess <@{0}>!\nGuess with:   >hm (letter)".format(author_id)
            blanks = "\n\n"
            for i in range(len(selected_word)):
                if guessed[i]:
                    blanks += selected_word[i]+" "
                else:
                    blanks += "_ "
            await ctx.send(msg)
            await ctx.send(self.hangman_states[stage]+blanks+"\nMissed:   "+ " ".join(missed)+"```")

        elif author_id in self.hangman_cache.keys() and letter:
            if letter == "quit":
                self.hangman_cache.pop(author_id, None)
                await ctx.send("Successfully quit!")
                return
            letter = list(letter)[0].upper()
            blanks = ""
            missed = self.hangman_cache[author_id][3]
            guessed = self.hangman_cache[author_id][2]
            selected_word = self.hangman_cache[author_id][1]
            stage = self.hangman_cache[author_id][0]
            found = False

            for i in range(len(selected_word)):
                if guessed[i]:
                    blanks += selected_word[i]+" "
                else:
                    blanks += "_ "

            if letter in missed or letter in blanks:
                await ctx.send("You've already guessed that letter!")
                await ctx.send(self.hangman_states[stage]+"\n\n"+blanks+"\nMissed:   " + " ".join(missed)+"```")
                return

            elif stage < 7:
                blanks = "\n\n"
                for i in range(len(selected_word)):
                    if selected_word[i] == letter:
                        guessed[i] = True
                        found = True
                if not found:
                    missed.append(letter)
                    self.hangman_cache[author_id][0] += 1
                    stage += 1
                    
                for i in range(len(selected_word)):
                    if guessed[i]:
                        blanks += selected_word[i]+" "
                    else:
                        blanks += "_ "

                if 0 not in guessed:
                    blanks = "\n\n" + ' '.join(selected_word)
                    await ctx.send("Hurrah for <@{0}>, you've saved the day!".format(author_id))
                    await ctx.send(self.hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")
                    self.hangman_cache.pop(author_id, None)
                    return   

                if self.hangman_cache[author_id][0] == 7:
                    blanks = "\n\n" + ' '.join(x for x in selected_word)
                    await ctx.send("You've let him hang <@{0}>, how could you...".format(author_id))
                    await ctx.send(self.hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")
                    self.hangman_cache.pop(author_id, None)
                    return
        
            await ctx.send("Take another guess <@{0}>!".format(author_id)) 
            await ctx.send(self.hangman_states[stage]+blanks+"\nMissed:   " + " ".join(missed)+"```")


        elif author_id in self.hangman_cache.keys() and not letter:
            embed.title = "Hangman"
            embed.description = "Usage:   >hangman (letter)"
            await ctx.send(embed=embed)


    @commands.command(pass_context=True)
    async def roll(self, ctx, roll_string):
        params = roll_string.split('d')
        if int(params[0]) > 10:
            await ctx.reply("Please keep the number of rolls to 10 and under!")
            return
        nums = ["roll {0}:\t{1}\n".format(x+1, randrange(int(params[1]))+1) if x < 9 else "roll {0}:   {1}\n".format(x+1, randrange(int(params[1]))+1) for x in range(int(params[0])) ]
        output = "```{0}```".format(''.join(nums))
        await ctx.send(output)

def setup(bot):
    bot.add_cog(GamesCog(bot))
