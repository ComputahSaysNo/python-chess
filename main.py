from board import *

def main():
    board = Board(BOARD_DIMENSIONS[0],BOARD_DIMENSIONS[1])
    board.load_start_board(STARTING_BOARD)
    target = board.get_piece("a2")
    board.check_valid_move("a2","a3")

if __name__ == '__main__':
    main()