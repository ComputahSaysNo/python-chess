from constants import *
from exceptions import *


def algebraic_to_xy(algebraic):
    """Converts algebraic notation to raw x and y positions (0-7 each)"""
    if len(algebraic) != 2:
        raise ValueError
    return ALPHABET.index(algebraic[0]), int(algebraic[1]) - 1


def xy_to_algebraic(x, y):
    """Takes in raw x and y positions and returns the equivalent in algebraic notation """
    return ALPHABET[x] + str(y + 1)


class Piece:
    """This class holds a single piece on the board, keeps track of its basic info like position, type, colour"""

    def __init__(self, piece_type, file, rank, colour):
        self.file = file
        self.rank = rank
        self.displayPos = ""
        self.update_display_pos()
        self.type = piece_type
        self.colour = colour
        self.isCaptured = False

    def update_display_pos(self):
        self.displayPos = ALPHABET[self.file] + str(self.rank + 1)


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
            if piece[0].islower():
                colour = BLACK
            self.pieces.append(Piece(piece[0].upper(), ALPHABET.index(piece[1]), int(piece[2]) - 1, colour))

    def get_piece(self, target_pos):
        """
        Gets a piece by its algebraic position (e.g. a1 or c8)
        """
        target_pos = target_pos.lower()
        for piece in self.pieces:
            if piece.displayPos == target_pos and not piece.isCaptured:
                return piece
        raise PieceNotFound

    def is_empty(self, pos):
        """Takes in a board square and returns True if the square isn't occupied"""
        try:
            self.get_piece(pos)
            return False
        except PieceNotFound:
            return True

    def check_valid_move(self, start_pos, end_pos, force_piece=False):
        """Takes in a start pos and end pos in algebraic notation and returns if that is a valid move or not"""
        if start_pos == end_pos:
            return False  # If the start pos is the same as the end the move isn't valid
        try:
            start_piece = self.get_piece(start_pos)  # If there isn't a piece at the start position the move isn't valid
        except PieceNotFound:
            return False  # If there is no piece at the start pos, the move isn't valid
        try:
            end_piece = self.get_piece(end_pos)
            if end_piece.colour == start_piece.colour:
                return False  # If the end piece is the same colour as the start piece, the move is invalid
        except PieceNotFound:
            pass
        end_xy = algebraic_to_xy(end_pos)
        if 0 > end_xy[0] > self.dimensions[0] - 1 or 0 > end_xy[1] > self.dimensions[1] - 1:
            return False  # If the destination square is outside the board, the move is invalid
        start_xy = (start_piece.file, start_piece.rank)
        difference = (end_xy[0] - start_xy[0], end_xy[1] - start_xy[1])
        valid_moves = []
        if not force_piece:
            start_type = start_piece.type
        else:
            start_type = force_piece

        if start_type == PAWN:
            # This bit can probably be written better. Pawn movement is HARD
            if start_piece.colour == WHITE:
                if self.is_empty(xy_to_algebraic(start_piece.file, start_piece.rank + 1)):
                    valid_moves = [(0, 1)]
                    if self.is_empty(
                            xy_to_algebraic(start_piece.file, start_piece.rank + 2)) and start_piece.rank == 1:
                        valid_moves.append((0, 2))
                try:
                    pawn_capture = self.get_piece(xy_to_algebraic(start_piece.file + 1, start_piece.rank + 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((1, 1))
                except PieceNotFound:
                    pass
                try:
                    pawn_capture = self.get_piece(xy_to_algebraic(start_piece.file - 1, start_piece.rank + 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((-1, 1))
                except PieceNotFound:
                    pass
            elif start_piece.colour == BLACK:
                if self.is_empty(xy_to_algebraic(start_piece.file, start_piece.rank - 1)):
                    valid_moves = [(0, -1)]
                    if self.is_empty(
                            xy_to_algebraic(start_piece.file, start_piece.rank - 2)) and start_piece.rank == 6:
                        valid_moves.append((0, -2))
                try:
                    pawn_capture = self.get_piece(xy_to_algebraic(start_piece.file - 1, start_piece.rank - 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((-1, -1))
                except PieceNotFound:
                    pass
                try:
                    pawn_capture = self.get_piece(xy_to_algebraic(start_piece.file + 1, start_piece.rank - 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((1, -1))
                except PieceNotFound:
                    pass

        elif start_type == KNIGHT:
            valid_moves = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]

        elif start_type == KING:
            valid_moves = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]

        if start_type in (PAWN, KNIGHT, KING):
            return difference in valid_moves
        # Pieces that we need to check for stuff in the way.

        if start_type == BISHOP:
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

        elif start_type == ROOK:
            if 0 not in difference:
                return False
            if difference[0] > 0:
                direction = (1, 0)
            elif difference[0] < 0:
                direction = (-1, 0)
            elif difference[1] > 0:
                direction = (0, 1)
            else:
                direction = (0, -1)
        check_pos = (start_piece.file, start_piece.rank)
        visited = []

        if start_type in (BISHOP, ROOK):
            for i in range(abs(sorted(difference)[1]) - 1):
                check_pos = (check_pos[0] + direction[0], check_pos[1] + direction[1])
                visited.append(self.is_empty(xy_to_algebraic(check_pos[0], check_pos[1])))
            return False not in visited

        elif start_type == QUEEN:
            return self.check_valid_move(start_pos, end_pos, BISHOP) or self.check_valid_move(start_pos, end_pos, ROOK)

    def make_move(self, start_pos, end_pos):
        if not self.check_valid_move(start_pos, end_pos):
            raise InvalidMoveError
        try:
            destination_piece = self.get_piece(end_pos)
            destination_piece.isCaptured = True
            self.capturedPieces.append(destination_piece)
        except PieceNotFound:
            pass
        start_piece = self.get_piece(start_pos)
        start_piece.file, start_piece.rank = (algebraic_to_xy(end_pos))
        start_piece.update_display_pos()
        if start_piece.type == PAWN:
            if (start_piece.colour == WHITE and start_piece.rank == 7) or (
                            start_piece.colour == BLACK and start_piece.rank == 0):
                start_piece.type = QUEEN

    def get_all_valid_moves(self, start_pos):
        output = []
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                end_pos = ALPHABET[x] + str(y + 1)
                if self.check_valid_move(start_pos, end_pos):
                    output.append(end_pos)
        return output
