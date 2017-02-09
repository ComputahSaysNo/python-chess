from constants import *
from exceptions import *
from game import xy_to_algebraic


def print_board_text(board):
    output = []
    for y in range(board.dimensions[1] + 1):
        row = ""
        for x in range(board.dimensions[0] + 1):
            row += TEXT_GUI_PADDING.split()[0]
            try:
                target = board.get_piece(xy_to_algebraic(x, y))
                if target.colour == WHITE:
                    row += target.type.upper()
                else:
                    row += target.type.lower()
            except PieceNotFound:
                row += " "
            row += TEXT_GUI_PADDING.split()[1]
        output.append(row)

    for i in reversed(output):
        print(i)

    for piece in board.capturedPieces:
        if piece.colour == WHITE:
            print(piece.type.upper())
        else:
            print(piece.type.lower())
