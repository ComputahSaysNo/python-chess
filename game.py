from exceptions import *
from globvars import *


class Square:
    """A class representing a single square on the board, which can hold a piece."""

    def __init__(self, pos):  # Pos is a string of form "a1" or "c8"
        self.pos = pos
        self.piece = None
        if (ALPHABET.index(pos[0]) + int(pos[1])) % 2 == 0:
            self.colour = BLACK
        else:
            self.colour = WHITE


if __name__ == '__main__':
    class Piece:
        """A class representing a single piece on the board. Goes within a Square's piece attribute"""

        def __init__(self, start_square, type, colour):
            self.colour = colour
            self.type = type
            self.pos = start_square.pos
            self.currentSquare = start_square
            self.valid_moves = MOVEMENT_RULES[self.type]

        def check_valid_move(self, end_pos, board):
            # First update movement rules
            if self.type == PAWN:
                if self.colour == WHITE and self.pos[1] == "2"


class Board:
    """Stores the whole chess board as a list of squares"""

    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.dimensions = (width, height)
        self.squares = []
        for y in range(height):
            for x in range(width):
                self.squares.append(Square(ALPHABET[x] + str(y + 1)))
        self.load_pieces(STARTING_BOARD)

    def load_pieces(self, pieces):
        # Pieces format is "pa2 pb2" etc. [piece, file, rank]", separated by spaces. White is UPPER, Black is lower
        pieces = pieces.split(" ")
        for piece in pieces:
            target = self.get_square(piece[1:])
            if piece[0].isupper():
                target.piece = Piece(target, piece[0], WHITE)
            else:
                target.piece = Piece(target, piece[0].upper(), BLACK)

    def get_square(self, pos):
        for square in self.squares:
            if square.pos == pos:
                return square
        raise InvalidSquareError

    def move_piece(self, start_pos, end_pos, validate=True):  # move the piece in [start_square] to [end_square]
        start_square = self.get_square(start_pos)
        end_square = self.get_square(end_pos)
        target = start_square.piece
        end_square.piece = target
        start_square.piece = None
