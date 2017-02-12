from constants import *
from exceptions import *
from board import xy_to_algebraic


def print_board_text(board):
    x_header = "   " + " ".join([ALPHABET[i]+" " for i in range(0,board.dimensions[0])])
    output = [x_header]
    for y in range(board.dimensions[1]):
        row = str(y+1) + " "
        for x in range(board.dimensions[0]):
            row += TEXT_GUI_PADDING.split()[0]
            try:
                target = board.get_piece(xy_to_algebraic(x, y))
                row += DISPLAY_PIECES[target.colour][target.type]
            except PieceNotFound:
                row += " "
            row += TEXT_GUI_PADDING.split()[1]
        row += " " + str(y+1)
        output.append(row)
    output.append(x_header)
    for i in reversed(output):
        print(i)

    for piece in board.capturedPieces:
        if piece.colour == WHITE:
            print(piece.type.upper())
        else:
            print(piece.type.lower())
