from constants import *
from exceptions import *


def algebraic_to_xy(pos):
    return ALPHABET.index(pos[0]) + 1, int(pos[1])


def xy_to_algebraic(x, y):
    return ALPHABET[x - 1] + str(y)


def rev_dict(dictionary):
    return dict((v, k) for k, v in dictionary.items())


class Piece:
    """A class holding a single piece on the board. Tracks its own type, colour and position"""

    def __init__(self, piece_type, pos, colour):
        self.type = piece_type
        self.pos = pos
        self.colour = colour
        self.x, self.y = algebraic_to_xy(self.pos)  # Remember to update these each time pos is changed.


class Board:
    """A class representing the chess board."""

    def __init__(self):
        self.activePieces = []
        self.capturedPieces = []
        self.activeColour = WHITE  # i.e. this colour is about to move
        self.inCheck = None
        self.canCastle = {WHITE: {KINGSIDE: False, QUEENSIDE: False}, BLACK: {KINGSIDE: False, QUEENSIDE: False}}
        self.enPassantTarget = ""
        self.halfMoveClock = 0  # Tracks the number of half-moves since the last pawn movement or piece capture
        self.moveClock = 0
        self.result = "IN PROGRESS"

    def load_fen(self, fen):
        """Loads a chess board in Forsyth-Edwards notation."""
        fen = fen.split(" ")  # Splits the FEN into its 6 fields.
        ranks = fen[0].split("/")
        rank_pointer = 8
        for rank in ranks:
            file_pointer = 1
            for char in rank:
                if char.isdigit():
                    file_pointer += int(char)
                else:
                    colour = WHITE
                    if char.islower():
                        colour = BLACK
                    self.activePieces.append(
                        Piece(FEN_PIECE_ALIASES[char.upper()], xy_to_algebraic(file_pointer, rank_pointer), colour))
                    file_pointer += 1
            rank_pointer -= 1
        self.activeColour = FEN_COLOUR_ALIASES[fen[1].upper()]
        self.canCastle = {WHITE: {KINGSIDE: False, QUEENSIDE: False}, BLACK: {KINGSIDE: False, QUEENSIDE: False}}
        for char in fen[2]:
            colour = WHITE
            if char.islower():
                colour = BLACK
            self.canCastle[colour][FEN_CASTLING_ALIASES[char.upper()]] = True
        self.enPassantTarget = fen[3]
        self.halfMoveClock = fen[4]
        self.moveClock = fen[5]

    def export_fen(self):
        output = ""
        for rank_pointer in range(BOARD_HEIGHT, 0, -1):
            rank = ""
            gap_counter = 0
            for file_pointer in range(1, BOARD_WIDTH + 1):
                pos = xy_to_algebraic(file_pointer, rank_pointer)
                try:
                    new = self.get_piece(pos)
                except PieceNotFound:
                    gap_counter += 1
                else:
                    if gap_counter != 0:
                        rank += str(gap_counter)
                        gap_counter = 0
                    if new.colour == WHITE:
                        rank += rev_dict(FEN_PIECE_ALIASES)[new.type].upper()
                    else:
                        rank += rev_dict(FEN_PIECE_ALIASES)[new.type].lower()
            if gap_counter != 0:
                rank += str(gap_counter)
            output += rank + "/"
        output = output[:-1]  # To remove trailing backslash at the end
        output += " " + rev_dict(FEN_COLOUR_ALIASES)[
            self.activeColour].lower() + " " + "KQkq" + " " + self.enPassantTarget + " " + str(
            self.halfMoveClock) + " " + str(
            self.moveClock)
        return output

    def get_piece(self, pos):
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

    def check_valid_move(self, start_pos, end_pos, force_piece=None, check_check=True):
        """Takes in a start and end position and returns if it is a valid move or not (Long Algebraic Notation)"""
        if start_pos == end_pos:
            return False  # Invalid move because nothing has been moved

        try:
            piece_to_move = self.get_piece(start_pos)
        except PieceNotFound:
            return False  # Invalid move if there isn't a piece at the start position
        else:
            piece_type = piece_to_move.type
            colour = piece_to_move.colour

        try:
            end_piece = self.get_piece(end_pos)
        except PieceNotFound:
            pass
        else:
            if end_piece.colour == colour:
                return False  # You can't capture your own pieces

        start_x, start_y = algebraic_to_xy(start_pos)
        end_x, end_y = algebraic_to_xy(end_pos)
        difference = (end_x - start_x, end_y - start_y)

        if end_x > BOARD_WIDTH or end_y > BOARD_HEIGHT:
            return False  # End position outside of board

        if force_piece is not None:
            piece_type = force_piece

        if piece_type in (PAWN, KNIGHT, KING):

            valid_moves = []

            if piece_type == PAWN:
                if colour == WHITE:
                    direction = 1
                    home_rank = 2
                else:
                    direction = -1
                    home_rank = 7
                if self.is_empty(xy_to_algebraic(start_x, start_y + direction)):
                    valid_moves.append((0, direction))
                    if self.is_empty(xy_to_algebraic(start_x, start_y + direction * 2)) and start_y == home_rank:
                        valid_moves.append((0, direction * 2))
                for i in (1, -1):
                    capture_pos = xy_to_algebraic(start_x + i, start_y + direction)
                    try:
                        target = self.get_piece(capture_pos)
                    except PieceNotFound:
                        pass
                    else:
                        if target.colour != colour:
                            valid_moves.append((i, direction))

            elif piece_type == KNIGHT:
                valid_moves = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]

            elif piece_type == KING:
                valid_moves = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]

            if difference not in valid_moves:
                return False

        elif piece_type in (BISHOP, ROOK, QUEEN):

            direction = [0, 0]

            if piece_type == BISHOP:
                if abs(difference[0]) != abs(difference[1]):
                    return False

            elif piece_type == ROOK:
                if 0 not in difference:
                    return False

            elif piece_type == QUEEN:
                piece_types = (BISHOP, ROOK)  # If it is a queen we just run the function again as a bishop and rook
                results = []
                for i in piece_types:
                    results.append(self.check_valid_move(start_pos, end_pos, force_piece=i))
                if True not in results:
                    return False

            for i in range(len(difference)):
                if difference[i] > 0:
                    direction[i] = 1
                elif difference[i] < 0:
                    direction[i] = -1
                else:
                    direction[i] = 0
            pos_to_check = (start_x, start_y)
            length_to_check = sorted((abs(difference[0]), abs(difference[1])))[1] - 1
            visited = []
            for i in range(length_to_check):
                pos_to_check = (pos_to_check[0] + direction[0], pos_to_check[1] + direction[1])
                visited.append(pos_to_check)
            for square in visited:
                if not self.is_empty(xy_to_algebraic(square[0], square[1])):
                    return False

        if check_check:
            test_board = Board()
            test_board.load_fen(self.export_fen())
            test_board.make_move(start_pos, end_pos, check_valid=False)
            if test_board.check_check() == colour:
                return False

        return True

    def make_move(self, start_pos, end_pos, check_valid=True, pawn_promotion=QUEEN):
        try:
            target = self.get_piece(start_pos)
        except PieceNotFound:
            raise InvalidMoveError
        if check_valid:
            if not self.check_valid_move(start_pos, end_pos):
                raise InvalidMoveError
        try:
            end_piece = self.get_piece(end_pos)
        except PieceNotFound:
            if target.type != PAWN:
                self.halfMoveClock += 1
            else:
                self.halfMoveClock = 0
        else:
            self.capturedPieces.append(end_piece)
            self.activePieces.remove(end_piece)
            self.halfMoveClock = 0
        target.pos = end_pos
        target.x, target.y = algebraic_to_xy(end_pos)
        if target.type == PAWN:
            if (target.y == 8 and target.colour == WHITE) or (target.y == 1 and target.colour == BLACK):
                target.type = pawn_promotion
        self.inCheck = self.check_check()

    def check_check(self):
        for colour in (WHITE, BLACK):
            target_king = None
            for piece in self.activePieces:
                if piece.type == KING and piece.colour == colour:
                    target_king = piece
            for attacker in self.activePieces:
                if attacker.colour != colour:
                    if self.check_valid_move(attacker.pos, target_king.pos, check_check=False):
                        return colour
        return None
