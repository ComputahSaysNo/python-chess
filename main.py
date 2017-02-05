from game import *

def main():
    board = Board()
    for i in board.squares:
        print(i.pos)
        if i.piece is not None:
            print(PIECE_NAMES[i.piece.type],COLOUR_NAMES[i.piece.colour])
        else:
            print("Empty")

if __name__ == '__main__':
    main()

