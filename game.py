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

    def __init__(self, square, type, colour):
        self.colour = colour
        self.type = type
        self.pos = (square.file, square.rank)
        self.currentSquare = square
