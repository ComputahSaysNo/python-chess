from game import *

def main():
    board = Board()
    for i in board.squares:
        print(i.pos)

if __name__ == '__main__':
    main()

