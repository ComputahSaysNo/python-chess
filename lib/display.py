import os

import pygame

from lib.board import *


def print_board(fen):
    x_header = "   a  b  c  d  e  f  g  h"
    board = fen.split()[0]
    ranks = board.split("/")
    output = [x_header]
    rank_counter = 8
    for rank in ranks:
        new_row = str(rank_counter) + " "
        for char in rank:
            if char.isdigit():
                for i in range(int(char)):
                    new_row += "[ ]"
            else:
                new_row += "[" + char + "]"
        new_row += " " + str(rank_counter)
        output.append(new_row)
        rank_counter -= 1
    output.append(x_header)
    for i in output:
        print(i)

