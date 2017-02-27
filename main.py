from lib.game import *
from tkinter import filedialog
import tkinter as tk
import time

def test():
    board = Board()
    board.load_fen(START_BOARD)
    print_board(board.export_fen())

def load_pgn(location, display=True):
    pgn = open(location, "rt")
    lines = []
    for line in pgn:
        lines.append(line.split())
    moves = []
    comment = False
    for line in lines:
        for part in line:
            if not comment:
                if part[0] == PGN_OPEN_COMMENT:
                    comment = True
                    if part[-1] == PGN_CLOSE_COMMENT:
                        comment = False
                    continue
                moves.append(part)
            else:
                if part[-1] == PGN_CLOSE_COMMENT:
                    comment = False
    board = Board()
    board.load_fen(START_BOARD)
    for move in moves:
        if move in (WHITE_WIN, BLACK_WIN, DRAW):
            board.result = move
            break
        if move == str(board.moveClock) + ".":
            continue
        if move[:len(str(board.moveClock)) + 1] == str(board.moveClock) + ".":
            move = move[len(str(board.moveClock)) + 1:]
        start, end = san_to_lan(board.export_fen(), move)
        board.make_move(start, end)
        if display:
            print(move)
            print_board(board.export_fen())

    print(board.check_game_outcome())
    print_board(board.export_fen())

def main():
    board = Board()
    board.load_fen(START_BOARD)
    current_player = board.activeColour
    if current_player == WHITE:
        waiting_player = BLACK
    else:
        waiting_player = WHITE
    print_board(board.export_fen())
    while True:
        print(board.gen_pseudo_valid_moves("a5"))
        print(board.enPassantTarget)
        toggle_player = False
        print("It's " + str(current_player) + "'s turn")
        move = str(input("Enter the move: "))
        if move == "fen":
            print(board.export_fen())
        elif move == "pass":
            toggle_player = True
        else:
            try:
                start, end = san_to_lan(board.export_fen(), move)
            except AmbiguousSAN:
                print("Ambiguous SAN, specify rank/file of start piece")
            except ValueError:
                print("Invalid move")
                continue
            else:
                try:
                    board.make_move(start, end)
                except InvalidMoveError:
                    print("Invalid Move")
                    continue
                else:
                    toggle_player = True
        if toggle_player:
            print_board(board.export_fen())
            bucket = current_player
            current_player = waiting_player
            waiting_player = bucket
            outcome = board.check_game_outcome()
            print(outcome)
            if outcome != IN_PROGRESS:
                break
            print(board.export_fen())
if __name__ == '__main__':
    start_time = time.time()
    load_pgn("lib/test_pgn/test.pgn", False)
    print(time.time()-start_time)