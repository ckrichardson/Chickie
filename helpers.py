import asyncio
from bs4 import BeautifulSoup
from copy import deepcopy
import datetime
from discord.ext import commands
import discord as discord
import hashlib
import io
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont
import pyowm
import random
import requests
import smtplib
import text
import time
import unicodedata
import urllib
import wikipedia

board_cache = dict()


async def get_aqi():
    url = "https://website-api.airvisual.com/v1/stations/by/cityID/ufjg8HsG3DZc9oFZ3?sortBy=aqi"
    r = requests.get(url)
    q = json.loads(r.content)
    c = 0
    for element in q:
        if element["id"] == "0442ef140ecc4b217c0c":
            return element["aqi"]


async def convert_board(board):
    converted_board = '`  1  2  3`\n'
    for i in range(len(board)):
        converted_board += "`{0}`".format(str(i+1))
        for j in range(len(board)):
            c = board[i][j]
            if c =='.':
                converted_board += ":black_square_button:"
            elif c == 'X':
                converted_board += ":negative_squared_cross_mark:"
            elif c == 'O':
                converted_board += ":red_circle:"
        converted_board += "\n"
    return converted_board


async def check_victory(board):
    victory_bool = await check_rows_cols(board)
    if victory_bool:
        return True
    
    victory_bool = await check_diags(board)
    if victory_bool:
        return True

    return False


async def check_draw(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == '.':
                return False
    return True

async def check_rows_cols(board):
    rows = []
    cols = []
    for i in range(3):
        rows = ''.join(board[i][x] for x in range(3))
        cols = ''.join(board[x][i] for x in range(3))
        
        if len(set(rows)) == 1:
            if 'X' in rows or 'O' in rows:
                return True
        
        if len(set(cols)) == 1:
            if 'X' in cols or 'O' in cols:
                return True
        
    return False


async def check_diags(board):
    diag_one = [board[x][x] for x in range(3)]
    diag_two = [board[2-y][y] for y in range(3)]

    if len(set(diag_one)) == 1:
        if 'X' in diag_one or 'O' in diag_one:
            return True
    if len(set(diag_two)) == 1:
        if 'X' in diag_two or 'O' in diag_two:
            return True

    return False


async def minmax(board, depth, max_player):
    global board_cache
    game_over = await check_victory(board)
    draw = await check_draw(board)
    # print(depth)
    board_hash = ''.join(element for row in board for element in row)+str(max_player)
    if game_over:
        # ttt.print_board(board)
        return [-10,10][depth % 2] - 1/depth*(-1)**(max_player), None, None
    if draw:
        return 0, None, None
    if board_hash in board_cache.keys():
        return board_cache[board_hash]

    if not max_player:
        valid_moves = []
        val = float("-inf")
        i_b,j_b = 0,0
        for i in range(3):
            for j in range(3):
                if board[i][j] != 'O' and board[i][j] != 'X':
                    board_with_move = deepcopy(board)
                    board_with_move[i][j] = ["O","X"][max_player]
                    r = await minmax(board_with_move, depth+1, True)
                    # print(r)
                    if val < r[0]:
                        val = r[0]
                        valid_moves = [(r[0],i,j)]
                        board_cache[board_hash] = (r[0],i,j)
                    elif val == r[0]:
                        valid_moves.append((r[0],i,j))
                        board_cache[board_hash] = (r[0],i,j)
        # print(val,i_b,j_b)
        return random.choice(valid_moves)
    else:
        valid_moves = []
        val = float("inf")
        i_b,j_b = 0,0
        for i in range(3):
            for j in range(3): 
                if board[i][j] != 'O' and board[i][j] != 'X':
                    board_with_move = deepcopy(board)
                    board_with_move[i][j] = ["O","X"][max_player]
                    r = await minmax(board_with_move, depth+1, False)
                    # print(r)
                    if val > r[0]:
                        val = r[0]
                        valid_moves = [(r[0],i,j)]
                        board_cache[board_hash] = (r[0],i,j)
                    elif val == r[0]:
                        valid_moves.append((r[0],i,j))
                        board_cache[board_hash] = (r[0],i,j)
        # print(val,i_b,j_b)
        return random.choice(valid_moves)


async def get_covid_data():
    r = requests.get("https://www.unr.edu/coronavirus/dashboard")
    data = r.content
    soup = BeautifulSoup(data, "html.parser")
    update_soup = BeautifulSoup(data, "html.parser")

    p_fields = soup.find_all('p', class_='large-body-copy')
    # print(p_fields)
    update_info = update_soup.find('em').get_text()
    nums = [unicodedata.normalize("NFKD", x.get_text().replace(",","")) for x in p_fields]

    s_active_data, s_recovered_data, s_total_data = nums[6].split('('), nums[7].split('('), nums[8].split('(')
    f_active_data, f_recovered_data, f_total_data = nums[9].split('('), nums[10].split('('), nums[11].split('(')

    s_active, s_recovered, s_total = int(s_active_data[0]), int(s_recovered_data[0]), int(s_total_data[0])
    f_active, f_recovered, f_total = int(f_active_data[0]), int(f_recovered_data[0]), int(f_total_data[0])

    active, recovered, total = s_active+f_active, s_recovered+f_recovered, s_total+f_total

    return (active, recovered, total, update_info)


async def get_insult():
    r = requests.get("https://evilinsult.com/generate_insult.php?type=plain&lang=en")
    return r.content.decode()


async def create_sanic_image(text):
    font_path = os.getcwd() + "/resources/fonts/Roboto-Bold.ttf"
    image_path = os.getcwd() + "/resources/images/sanic.jpg"
    k = ''.join(text).split(" ")
    image  = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    x, y = 45, 200
    color = 'rgb(255,255,255)'
    message = ""
    chars = 0
    font = ImageFont.truetype(font_path, size=70)

    limit = 20
    line = 0

    for i in range(len(k)):
        if line > 0:
            limit = 21
        if i > 1:
            limit = 22

        current_word = k[i] 
        len_word = len(current_word)
        if chars+len_word+1 > limit:
            draw.text((x,y), message,  fill=color, font=font)
            y += 105
            chars = len_word+1
            message = current_word + " "
            line += 1
        else:
            message += current_word + " "
            chars += len_word+1

    draw.text((x,y), message, fill=color, font=font)

    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format="JPEG")

    return img_byte_array


async def get_hm_states():
    return {0: text.hangman_0, 1: text.hangman_1, \
            2: text.hangman_2, 3: text.hangman_3, \
            4: text.hangman_4, 5: text.hangman_5, \
            6: text.hangman_6, 7: text.hangman_7}


async def get_quotes():
    with open(os.getcwd()+"/resources/quotes.json", "r") as quotes_file:
        quotes = json.loads(quotes_file.read())
        return quotes


async def get_blacklist():
    with open(os.getcwd()+"/resources/blacklist.txt", "r") as bl:
        blacklist = [int(x) for x in bl]
        return blacklist

