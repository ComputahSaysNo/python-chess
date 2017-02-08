from constants import *
from exceptions import *


class Piece:
    """This class holds a single piece on the board, and checks its own movement"""

    def __init__(self, piece_type, file, rank, colour):
        self.file = file
        self.rank = rank
        self.displayPos = ALPHABET[file] + str(rank)
        self.type = piece_type
        self.colour = colour


class Board:
    """Class holding all the board pieces in a list"""

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.pieces = []
        self.capturedPieces = []
        self.load_pieces(STARTING_BOARD)

    def load_pieces(self, pieces):
        """
        Format for this function is "pa1 Nf2" etc. where the first character in each block is the piece type and the
        second and third are its position in algebraic notation.
        See constants.py for the piece aliases. UPPERCASE is white, lowercase is black.
        """
        pieces = pieces.split()
        for piece in pieces:
            if len(piece) != 3:
                raise InvalidPieceList
            colour = WHITE
            if colour[0].isupper():
                colour = BLACK
            self.pieces.append(Piece(piece[0].upper(), ALPHABET.index(piece[1]), piece[2], colour))
