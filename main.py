from game import *
from display import *

def main():
    board = Board()
    for i in board.pieces:
        print(i.type, i.displayPos)
    new = board.get_piece("h8")

if __name__ == '__main__':
    main()

