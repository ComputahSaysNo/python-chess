from constants import *
from exceptions import *


def algebraic_to_xy(algebraic):
    """Converts algebraic notation to raw x and y positions (0-7 each)"""
    if len(algebraic) != 2 or not algebraic[0].isalpha() or not algebraic[1].isdigit():
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
        self.timesMoved = 0

    def update_display_pos(self):
        self.displayPos = ALPHABET[self.file] + str(self.rank + 1)


class Board:
    """Class holding all the board pieces in a list. Piece movement is handled at this level"""

    def __init__(self, width, height, pieces):
        self.dimensions = (width, height)
        self.pieces = []
        self.capturedPieces = []
        self.load_pieces(pieces)
        self.inCheck = {WHITE: False, BLACK: False}
        self.moves = ""

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

    def export_pieces(self):
        """Returns the pieces in the same format as used by load_pieces above."""
        output = ""
        for piece in self.pieces:
            if piece.colour == WHITE:
                output += piece.type.upper()
            else:
                output += piece.type.lower()
            output += piece.displayPos + " "
        return output

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

    def check_valid_move(self, start_pos, end_pos, colour, force_piece=False, check_check=True):
        """Takes in a start pos and end pos in algebraic notation and returns if that is a valid move or not"""
        output = False
        if start_pos == end_pos:
            return False  # If the start pos is the same as the end the move isn't valid
        try:
            start_piece = self.get_piece(start_pos)  # If there isn't a piece at the start position the move isn't valid
        except PieceNotFound:
            return False  # If there is no piece at the start pos, the move isn't valid
        if start_piece.colour != colour:
            return False
        try:
            end_piece = self.get_piece(end_pos)
            if end_piece.colour == start_piece.colour:
                return False  # If the end piece is the same colour as the start piece, the move is invalid
        except PieceNotFound:
            pass
        end_xy = algebraic_to_xy(end_pos)
        if 0 > end_xy[0] > self.dimensions[0] - 1 or 0 > end_xy[1] > self.dimensions[1] - 1:
            return False  # If the destination square is outside the board, the move is invalid
        if not force_piece:
            start_type = start_piece.type
        else:
            start_type = force_piece

        start_xy = (start_piece.file, start_piece.rank)
        difference = (end_xy[0] - start_xy[0], end_xy[1] - start_xy[1])

        if start_type in (PAWN, KNIGHT, KING):
            valid_moves = []

            if start_type == PAWN:
                if start_piece.colour == WHITE:
                    direction_multiplier = 1
                else:
                    direction_multiplier = -1
                if self.is_empty(xy_to_algebraic(start_piece.file, start_piece.rank + direction_multiplier * 1)):
                    valid_moves.append((0, direction_multiplier * 1))
                    if self.is_empty(xy_to_algebraic(start_piece.file, start_piece.rank + direction_multiplier * 2)):
                        if (start_piece.rank == 1 and start_piece.colour == WHITE) or (
                                        start_piece.rank == 6 and start_piece.colour == BLACK):
                            valid_moves.append((0, direction_multiplier * 2))
                try:
                    pawn_capture = self.get_piece(
                        xy_to_algebraic(start_piece.file + 1, start_piece.rank + direction_multiplier * 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((1, 1))
                except PieceNotFound:
                    pass
                try:
                    pawn_capture = self.get_piece(
                        xy_to_algebraic(start_piece.file - 1, start_piece.rank + direction_multiplier * 1))
                    if pawn_capture.colour != start_piece.colour:
                        valid_moves.append((-1, 1))
                except PieceNotFound:
                    pass

            elif start_type == KNIGHT:
                valid_moves = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]

            elif start_type == KING:
                valid_moves = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]

            output = difference in valid_moves

        # Pieces that we need to check for stuff in the way.
        if start_type in (BISHOP, ROOK):
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
            difference = sorted((abs(difference[0]), abs(difference[1])))
            for i in range(difference[1]-1):
                check_pos = (check_pos[0] + direction[0], check_pos[1] + direction[1])
                visited.append(self.is_empty(xy_to_algebraic(check_pos[0], check_pos[1])))
            output = False not in visited

        elif start_type == QUEEN:  # If it's a queen we just call the function again as a bishop or a rook.
            output = self.check_valid_move(start_pos, end_pos, colour, BISHOP) or self.check_valid_move(start_pos,
                                                                                                        end_pos, colour,
                                                                                                        ROOK)
        if output:
            if check_check:
                # Make a copy of the current board, make the c oposed move, if the move places the player in check it
                # is not valid.
                test_board = Board(self.dimensions[0], self.dimensions[1], self.export_pieces())
                test_board.make_move(start_pos, end_pos, colour, False)
                if test_board.inCheck[colour]:
                    return False
            return True
        else:
            return False

    def make_move(self, start_pos, end_pos, colour, check_valid=True):
        if check_valid:
            if not self.check_valid_move(start_pos, end_pos, colour):
                raise InvalidMoveError
        try:
            destination_piece = self.get_piece(end_pos)
            destination_piece.isCaptured = True
            self.capturedPieces.append(destination_piece)
            self.pieces.remove(destination_piece)
        except PieceNotFound:
            pass
        start_piece = self.get_piece(start_pos)
        start_piece.file, start_piece.rank = (algebraic_to_xy(end_pos))
        start_piece.update_display_pos()
        if start_piece.type == PAWN:
            if (start_piece.colour == WHITE and start_piece.rank == 7) or (
                            start_piece.colour == BLACK and start_piece.rank == 0):
                start_piece.type = QUEEN
        self.inCheck[WHITE] = self.check_check(WHITE)
        self.inCheck[BLACK] = self.check_check(BLACK)
        start_piece.timesMoved += 1

    def castle(self, colour, direction):
        if self.inCheck[colour]:
            raise InvalidMoveError  # You can't castle out of check
        if colour == WHITE:
            home_rank = 0
        else:
            home_rank = 7
        try:
            target_king = self.get_piece(xy_to_algebraic(4, home_rank))
        except PieceNotFound:
            raise InvalidMoveError
        else:
            if target_king.type != KING or target_king.timesMoved != 0:
                raise InvalidMoveError
        if direction == KINGSIDE:
            target_rook_file = 7
            direction_multiplier = 1
        elif direction == QUEENSIDE:
            target_rook_file = 0
            direction_multiplier = -1
        else:
            raise InvalidMoveError
        try:
            target_rook = self.get_piece(xy_to_algebraic(target_rook_file, home_rank))
        except PieceNotFound:
            raise InvalidMoveError
        else:
            if target_rook.type != ROOK or target_rook.timesMoved != 0:
                raise InvalidMoveError
        for file in range(target_king.file + direction_multiplier, target_rook.file, direction_multiplier):
            if not self.is_empty(xy_to_algebraic(file, home_rank)):
                raise InvalidMoveError

        test_board = Board(self.dimensions[0], self.dimensions[1], self.export_pieces())
        try:
            current_king_pos = target_king.displayPos
            for i in range(2):
                new_king_pos = xy_to_algebraic(algebraic_to_xy(current_king_pos)[0] + direction_multiplier, home_rank)
                test_board.make_move(current_king_pos, new_king_pos, colour)
                current_king_pos = new_king_pos
        except InvalidMoveError:
            raise InvalidMoveError
        else:
            if direction == KINGSIDE:
                self.make_move(target_king.displayPos, xy_to_algebraic(6, home_rank), colour, False)
                self.make_move(target_rook.displayPos, xy_to_algebraic(5, home_rank), colour, False)
            elif direction == QUEENSIDE:
                self.make_move(target_king.displayPos, xy_to_algebraic(2, home_rank), colour, False)
                self.make_move(target_rook.displayPos, xy_to_algebraic(3, home_rank), colour, False)

    def get_all_piece_moves(self, start_pos):
        output = []
        start_colour = self.get_piece(start_pos).colour
        for y in range(self.dimensions[1]):
            for x in range(self.dimensions[0]):
                end_pos = ALPHABET[x] + str(y + 1)
                if self.check_valid_move(start_pos, end_pos, start_colour):
                    output.append(end_pos)
        return output

    def check_check(self, colour):
        target = None
        for piece in self.pieces:
            if piece.type == KING and piece.colour == colour:
                target = piece
        if target is None:
            return False
        for attacker in self.pieces:
            if attacker.colour != colour:
                if self.check_valid_move(attacker.displayPos, target.displayPos, attacker.colour, False, False):
                    return True
        return False

    def check_checkmate(self, colour):
        """Returns if [colour] has been checkmated"""
        valid_moves = []
        for piece in self.pieces:
            if piece.colour == colour:
                piece_moves = self.get_all_piece_moves(piece.displayPos)
                for i in piece_moves:
                    valid_moves.append(i)
        if len(valid_moves) == 0 and self.check_check(colour):
            return True

    def check_stalemate(self, colour):
        """Returns if [colour] has been stalemated"""
        valid_moves = []
        for piece in self.pieces:
            if piece.colour == colour:
                piece_moves = self.get_all_piece_moves(piece.displayPos)
                for i in piece_moves:
                    valid_moves.append(i)
        if len(valid_moves) == 0 and not self.check_check(colour):
            return True
