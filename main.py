from game import *
from display import *

def main():
    board = Board()
    for i in board.pieces:
        print(i.type, i.displayPos)
if __name__ == '__main__':
    main()

