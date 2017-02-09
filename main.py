from game import *
from display import *

def main():
    board = Board()
    print_board_text(board)
    while True:
        move = str(input("Enter the start position and the end position of the move: ")).lower().split()
        try:
            board.make_move(move[0],move[1])
            print_board_text(board)
        except InvalidMoveError:
            print("Invalid move, try again")

if __name__ == '__main__':
    main()

