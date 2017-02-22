from lib.game import *
from tkinter import filedialog
import tkinter as tk

def file_save():
    root = tk.Tk()
    root.withdraw()
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = START_BOARD
    f.write(text2save)
    f.close() # `()` was missing.

def test():
    game = Game()
    game.load_pgn("lib/test_pgn/test.pgn")
    game.run_game(TEXT)

if __name__ == '__main__':
    test()
