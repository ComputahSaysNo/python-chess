from board import *

def main():
    board = Board()
    board.load_fen(START_BOARD)
    for i in board.activePieces:
        print(i.pos, i.type, i.colour)
    print(board.activeColour)
    print(board.canCastle)
    print(board.check_check())
    print(board.export_fen())
if __name__ == '__main__':
    main()