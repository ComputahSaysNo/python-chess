from constants import *
from exceptions import *


def algebraic_pos_to_file_rank(pos):
    """Takes in an algebraic pos like e5 and returns the rank and file"""
    if len(pos) != 2:
        raise ValueError
    return ALPHABET.index(pos[0]) + 1, int(pos[1])


def file_rank_to_algebraic_pos(file, rank):
    return ALPHABET[file - 1] + str(rank)


def reverse_dict(d):
    return dict((v, k) for k, v in d.items())


class Piece:
    """Piece class stores its own position, type and colour."""

    def __init__(self, piece_type, start_pos, colour):
        self.pos = start_pos
        self.type = piece_type
        self.colour = colour
        self.timesMoved = 0


class Board:
    """Holds multiple piece classes in a list and handles piece movement."""

    def __init__(self, width, height):
        self.dimensions = (width, height)
        self.activePieces = []
        self.capturedPieces = []
        self.inCheck = {WHITE: False, BLACK: False}

    def load_start_board(self, start_board):
        """Input to this method should be a string containing a list of pieces in algebraic notation (e.g. Nf1 Qe2).
        Use UPPERCASE for white and lowercase for black. Pawns need to use P as their symbol to distinguish black
        and white"""
        for piece in start_board.split():
            if len(piece) != 3:
                raise ValueError
            if piece[0].isupper():
                colour = WHITE
            else:
                colour = BLACK
            piece_type = PIECE_LOADING_ALIASES[piece[0].upper()]
            self.activePieces.append(Piece(piece_type, piece[1:], colour))

    def get_piece(self, pos):
        """Return a piece from its algebraic position (e.g. a1, e5)"""
        for piece in self.activePieces:
            if piece.pos == pos:
                return piece
        raise PieceNotFound

    def is_empty(self, pos):
        try:
            self.get_piece(pos)
        except PieceNotFound:
            return True
        else:
            return False

    def is_valid_pos(self, pos):
        if len(pos) == 2:
            if pos[0].isalpha() and pos[1].isdigit():
                xy = algebraic_pos_to_file_rank(pos)
                return xy[0] <= self.dimensions[0] and xy[1] < self.dimensions[1]
        return False

    def check_valid_move(self, start_pos, end_pos, check_check=False, force_piece=False):
        """Takes in a start and end position and returns whether that is a valid move"""
        if start_pos == end_pos:
            return False, "Start position is the same as end position"
        try:
            piece = self.get_piece(start_pos)
        except PieceNotFound:
            return False, "No piece at start position"
        if not self.is_valid_pos(end_pos):
            return False, "Invalid end position (outside of board)"
        colour = piece.colour
        try:
            end_piece = self.get_piece(end_pos)
        except PieceNotFound:
            pass
        else:
            end_colour = end_piece.colour
            if colour == end_colour:
                return False, "Cannot capture piece of own colour"
        piece_type = piece.type
        start_xy = algebraic_pos_to_file_rank(start_pos)
        end_xy = algebraic_pos_to_file_rank(end_pos)
        difference = (end_xy[0] - start_xy[0], end_xy[1] - start_xy[1])
        if piece_type == PAWN:
            valid_moves = []
            if colour == WHITE:
                direction = 1
                start_rank = 2
            else:
                direction = -1
                start_rank = 7
            if self.is_empty(piece.pos[0] + str(int(piece.pos[1]) + direction)):
                valid_moves.append((0, direction * 1))
                if self.is_empty(piece.pos[0] + str(int(piece.pos[1]) + direction * 2)) and int(
                        piece.pos[1]) == start_rank:
                    valid_moves.append((0, direction * 2))
            for i in (1, -1):
                capture_pos = ALPHABET[ALPHABET.index(piece.pos[0]) + i] + str(int(piece.pos[1]) + direction)
                if self.is_valid_pos(capture_pos):
                    try:
                        target = self.get_piece(capture_pos)
                    except PieceNotFound:
                        pass
                    else:
                        if target.colour != colour:
                            valid_moves.append((i, direction))
            if difference not in valid_moves:
                return False, "Invalid move for type PAWN"
        elif piece_type == KNIGHT:
            valid_moves = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
            if difference not in valid_moves:
                return False, "Invalid move for type KNIGHT"
        elif piece_type == KING:
            valid_moves = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
            if difference not in valid_moves:
                return False, "Invalid move for type KING"
        elif piece_type in (BISHOP, ROOK):
            direction = (0, 0)
            if piece_type == BISHOP:
                if abs(difference[0]) != abs(difference[1]):
                    return False
                if difference[0] > 0 and difference[1] > 0:
                    direction = (1, 1)
                elif difference[0] > 0 > difference[1]:
                    direction = (1, -1)
                elif difference[0] < 0 < difference[1]:
                    direction = (-1, 1)
                else:
                    direction = (-1, -1)
            elif piece_type == ROOK:
                if 0 not in difference:
                    return False
                if difference[0] > 0:
                    direction = (1, 0)
                elif difference[0] < 0:
                    direction = (-1, 0)
                elif difference[1] > 0:
                    direction = (0, 1)
                elif difference[1] < 0:
                    direction = (0, -1)
            pos_to_check = algebraic_pos_to_file_rank(start_pos)
            visited = []
            length_to_check = sorted((abs(difference[0]), abs(difference[1])))[1] - 1
            for i in range(length_to_check):
                pos_to_check = (pos_to_check[0] + direction[0], pos_to_check[1] + direction[1])
                visited.append(pos_to_check)
            for square in visited:
                if not self.is_empty(square):
                    return False, "Piece in the way of BISHOP/ROOK/QUEEN movement"
        elif piece_type == QUEEN:
            if not (self.check_valid_move(start_pos, end_pos, colour, force_piece=BISHOP) or self.check_valid_move(
                    start_pos, end_pos, colour, force_piece=ROOK)):
                return False, "Invalid move for type QUEEN"
        if check_check:
            pass

        return True

