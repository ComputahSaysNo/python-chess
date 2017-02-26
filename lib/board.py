from lib.constants import *
from lib.exceptions import *


def algebraic_to_xy(pos):
    return ALPHABET.index(pos[0]) + 1, int(pos[1])


def xy_to_algebraic(x, y):
    return ALPHABET[x - 1] + str(y)


def rev_dict(dictionary):
    return dict((v, k) for k, v in dictionary.items())


def check_valid_pos(pos):
    if len(pos) == 2 and pos[0].isalpha() and pos[1].isdigit():
        x, y = algebraic_to_xy(pos)
        return 0 < x <= BOARD_WIDTH and 0 < y <= BOARD_HEIGHT
    return False


class Piece:
    """A class holding a single piece on the board. Tracks its own type, colour and position"""

    def __init__(self, piece_type, pos, colour):
        self.type = piece_type
        self.pos = pos
        self.colour = colour
        self.x, self.y = algebraic_to_xy(self.pos)  # Remember to update these each time pos is changed.
        self.attackingSquares = []


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
        self.result = IN_PROGRESS
        self.currentValidMoves = {}
        self.validWithoutChecks = {}
        self.previousStates = []

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
        if fen[2] == FEN_EMPTY:
            pass
        else:
            for char in fen[2]:
                colour = WHITE
                if char.islower():
                    colour = BLACK
                self.canCastle[colour][FEN_CASTLING_ALIASES[char.upper()]] = True
        self.enPassantTarget = fen[3]
        self.halfMoveClock = int(fen[4])
        self.moveClock = int(fen[5])

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
        if self.canCastle == {WHITE: {KINGSIDE: False, QUEENSIDE: False}, BLACK: {KINGSIDE: False, QUEENSIDE: False}}:
            castle_availability = FEN_EMPTY
        else:
            castle_availability = ""
            for colour in (WHITE, BLACK):
                for direction in (KINGSIDE, QUEENSIDE):
                    if self.canCastle[colour][direction]:
                        if colour == WHITE:
                            castle_availability += rev_dict(FEN_CASTLING_ALIASES)[direction].upper()
                        else:
                            castle_availability += rev_dict(FEN_CASTLING_ALIASES)[direction].lower()
        output += " " + rev_dict(FEN_COLOUR_ALIASES)[
            self.activeColour].lower() + " " + castle_availability + " " + self.enPassantTarget + " " + str(
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

    def check_valid_move(self, start, end, check_check=True, force_type=None):
        if start == end:
            return False
        if end not in self.gen_pseudo_valid_moves(start):
            return False


    def gen_pseudo_valid_moves(self, start):
        try:
            target = self.get_piece(start)
        except PieceNotFound:
            return []
        output = []
        if target.type == PAWN:
            direction = 1 if target.colour == WHITE else -1
            home_rank = 2 if target.colour == WHITE else 7
            one_ahead = xy_to_algebraic(target.x, target.y + direction)
            if self.is_empty(one_ahead):
                output.append(one_ahead)
                two_ahead = xy_to_algebraic(target.x, target.y + 2 * direction)
                if self.is_empty(two_ahead) and target.y == home_rank:
                    output.append(two_ahead)
            for side in (1, -1):
                capture_pos = xy_to_algebraic(target.x + side, target.y + direction)
                if capture_pos == self.enPassantTarget:
                    output.append(capture_pos)
                try:
                    piece_to_capture = self.get_piece(capture_pos)
                except PieceNotFound:
                    pass
                else:
                    if piece_to_capture.colour != target.colour:
                        output.append(capture_pos)
        elif target.type == KNIGHT:
            knight_valid_diffs = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
            for diff in knight_valid_diffs:
                output.append(xy_to_algebraic(target.x + diff[0], target.y + diff[1]))
        elif target.type == KING:
            king_valid_diffs = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
            for diff in king_valid_diffs:
                output.append(xy_to_algebraic(target.x + diff[0], target.y + diff[1]))
        elif target.type in (BISHOP, ROOK, QUEEN):
            valid_directions = []
            if target.type == BISHOP:
                valid_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            elif target.type == ROOK:
                valid_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            elif target.type == QUEEN:
                valid_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
            for direction in valid_directions:
                current_pos = [target.x, target.y]
                while True:
                    new_pos = [current_pos[0] + direction[0], current_pos[1] + direction[1]]
                    if not check_valid_pos(xy_to_algebraic(new_pos[0], new_pos[1])):
                        break
                    if self.is_empty(xy_to_algebraic(new_pos[0], new_pos[1])):
                        output.append(xy_to_algebraic(new_pos[0], new_pos[1]))
                        current_pos = new_pos
                        continue
                    piece_in_way = self.get_piece(xy_to_algebraic(new_pos[0], new_pos[1]))
                    if piece_in_way.colour != target.colour:
                        output.append(xy_to_algebraic(new_pos[0], new_pos[1]))
                    break
        output_checked = []
        for i in output:
            if check_valid_pos(i):
                try:
                    end_piece = self.get_piece(i)
                except PieceNotFound:
                    pass
                else:
                    if end_piece.colour == target.colour:
                        continue
                output_checked.append(i)
        return output_checked
