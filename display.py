from globvars import *

def print_board_text(board):
    output = []
    for y in range(board.dimensions[1]):
        row = " "
        for x in range(board.dimensions[0]):
            target = board.get_square(ALPHABET[x] + str(y + 1))
            row += " " + TEXT_GUI_PADDING.split()[0]
            if target.piece is None:
                row += " "
            elif target.piece.colour == WHITE:
                row += target.piece.type.upper()
            else:
                row += target.piece.type.lower()
            row += TEXT_GUI_PADDING.split()[1]
        output.append(row)
    for row in reversed(output):
        print(row)