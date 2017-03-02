from lib.game import *
from lib.board import *
from lib.display import *
import sys


def test():
    board = Board()
    board.load_fen(START_BOARD)
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
    game = Game()
    game.new_game(event="Python match",white="test1",black="test2")
    game.load_pgn("lib/test_pgn/test.pgn")
    display = ChessGUI()
    display.view_moves(game)