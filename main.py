from game import *
from display import *

def main():
    board = Board()
    print_board_text(board)
    print("")
    board.move_piece(("e",1),("e",2))
    print_board_text(board)

if __name__ == '__main__':
    main()

