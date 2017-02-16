import pygame
import os
from lib.constants import *

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

class ChessGUI:

    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((128, 128))
        clock = pygame.time.Clock()

        counter, text = 10, '10'.rjust(3)
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        font = pygame.font.SysFont('Consolas', 30)
        car = pygame.image.load('img/pieces/white/king.png')
        print(pygame.font.get_fonts())

        while True:
            for e in pygame.event.get():
                if e.type == pygame.USEREVENT:
                    counter -= 1
                    text = str(counter).rjust(3) if counter > 0 else 'boom!'
                if e.type == pygame.QUIT: break
            else:
                screen.fill((255, 255, 255))
                screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
                screen.blit(car, (50, 50))
                pygame.display.flip()
                clock.tick(60)
                continue
            break

if __name__ == '__main__':
    gui = ChessGUI()
