from constants import *
from exceptions import *


class Piece:
    """This class holds a single piece on the board, keeps track of its basic info like position, type, colour"""

    def __init__(self, piece_type, file, rank, colour):
        self.file = file
        self.rank = rank
        self.displayPos = ALPHABET[file] + str(rank + 1)
        self.type = piece_type
        self.colour = colour


class Board:
    """Class holding all the board pieces in a list. Piece movement is handled at this level"""

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.dimensions = (width, height)
        self.pieces = []
        self.capturedPieces = []
        self.load_pieces(STARTING_BOARD)

    def load_pieces(self, pieces):
        """
        Format for this method is "pa1 Nf2" etc. where the first character in each block is the piece type and the
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
            self.pieces.append(Piece(piece[0].upper(), ALPHABET.index(piece[1]), int(piece[2]) - 1, colour))

    def get_piece(self, target_pos):
        """
        Gets a piece by its algebraic position (e.g. a1 or c8)
        """
        target_pos = target_pos.lower()
        for piece in self.pieces:
            if piece.displayPos == target_pos:
                return piece
        raise PieceNotFound

    def check_valid_move(self, start_pos, end_pos):
        """Takes in a start pos and end pos in algebraic notation and returns if that is a valid move or not"""
        try:
            start_piece = self.get_piece(start_pos)  # If there isn't a piece at the start position the move isn't valid
        except PieceNotFound:
            return False
        try:
            end_piece = self.get_piece(end_pos)
            if end_piece.colour == start_piece.colour:
                return False
        except PieceNotFound:
            pass
