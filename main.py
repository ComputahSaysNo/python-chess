from game import *
from display import *

def main():
    board = Board()
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            algebraic = ALPHABET[x] + str(y+1)
            if board.check_valid_move("a2",algebraic):
                print(algebraic)

if __name__ == '__main__':
    main()

