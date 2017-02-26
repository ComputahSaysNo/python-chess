from lib.game import *
from tkinter import filedialog
import tkinter as tk

def test():
    board = Board()
    board.load_fen(START_BOARD)
    print_board(START_BOARD)
    for piece in board.activePieces:
        print(piece.type, piece.pos, board.gen_pseudo_valid_moves(piece.pos))

if __name__ == '__main__':
    test()
