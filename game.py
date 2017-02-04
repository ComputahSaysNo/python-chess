from globvars import *


class Square:
    """A class representing a single square on the board, which can hold a piece."""

    def __init__(self, file, rank):  # File is a-h, rank is 1-8
        self.pos = (file, rank)
        self.piece = None
        if (ALPHABET.index(file) + rank) % 2 == 0:
            self.colour = WHITE
        else:
            self.colour = BLACK


class Piece:
    """A class representing a single piece on the board. Goes within a Square's piece attribute"""

    def __init__(self, start_square, type, colour):
        self.colour = colour
        self.type = type
        self.pos = (start_square.file, start_square.rank)
        self.currentSquare = start_square


class Board:
    """Stores the whole chess board as a list of squares"""

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.squares = []
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                self.squares.append(Square(ALPHABET[x], y + 1))
