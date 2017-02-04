from exceptions import *
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
        self.pos = start_square.pos
        self.currentSquare = start_square


class Board:
    """Stores the whole chess board as a list of squares"""

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.squares = []
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                self.squares.append(Square(ALPHABET[x], y + 1))
        self.load_pieces(STARTING_BOARD)

    def load_pieces(self, pieces):
        # Pieces format is "pa2 pb2" etc. [piece, file, rank]", separated by spaces. White is UPPER, Black is lower
        pieces = pieces.split(" ")
        for piece in pieces:
            target = self.get_square(piece[1], int(piece[2]))
            if piece[0].isupper():
                target.piece = Piece(target, PIECE_ALIASES[piece[0]], WHITE)
            else:
                target.piece = Piece(target, PIECE_ALIASES[piece[0].upper()], BLACK)

    def get_square(self, file, rank):
        for square in self.squares:
            if square.pos == (file, rank):
                return square
        raise InvalidSquareError
