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
        return x <= BOARD_WIDTH and y <= BOARD_HEIGHT
    return False


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
        self.result = IN_PROGRESS
        self.currentValidMoves = {}
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

    def get_all_valid_moves_from_pos(self, pos, check_check=True):
        start_x, start_y = algebraic_to_xy(pos)
        target_piece = self.get_piece(pos)
        valid_moves = []
        if target_piece.type in (PAWN, KNIGHT, KING):
            if target_piece.type == PAWN:
                if target_piece.colour == WHITE:
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
                    if capture_pos == self.enPassantTarget:
                        valid_moves.append((i, direction))
                    try:
                        target = self.get_piece(capture_pos)
                    except PieceNotFound:
                        pass
                    else:
                        if target.colour != target_piece.colour:
                            valid_moves.append((i, direction))

            elif target_piece.type == KNIGHT:
                valid_moves = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]

            elif target_piece.type == KING:
                valid_moves = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]

        elif target_piece.type in (BISHOP, ROOK, QUEEN):
            for y in range(BOARD_HEIGHT):
                for x in range(BOARD_WIDTH):
                    difference = (x + 1) - start_x, (y + 1) - start_y
                    if (target_piece.type == BISHOP or target_piece.type == QUEEN) and abs(difference[0]) == abs(
                            difference[1]):
                        valid_moves.append(difference)
                    if (target_piece.type == ROOK or target_piece.type == QUEEN) and 0 in difference:
                        valid_moves.append(difference)
        to_test = []
        for move in valid_moves:
            end_pos = (start_x + move[0], start_y + move[1])
            if 0 < end_pos[0] <= BOARD_WIDTH and 0 < end_pos[1] <= BOARD_HEIGHT:
                to_test.append(xy_to_algebraic(end_pos[0], end_pos[1]))
        output = []
        for end_pos in to_test:
            difference = (algebraic_to_xy(end_pos)[0] - start_x, algebraic_to_xy(end_pos)[1] - start_y)
            add = True
            if end_pos == pos:
                add = False
            try:
                end_piece = self.get_piece(end_pos)
            except PieceNotFound:
                pass
            else:
                if end_piece.colour == target_piece.colour:
                    add = False
            if target_piece.type in (BISHOP, ROOK, QUEEN):
                direction = [0, 0]
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
                        add = False
            if check_check and add:
                test_board = Board()
                test_board.load_fen(self.export_fen())
                test_board.make_move(pos, end_pos, check_valid=False, update_board_info=False)
                if test_board.check_check() == target_piece.colour:
                    add = False
            if add:
                output.append(end_pos)
        return output

    def get_all_valid_moves(self, check_check=True, check_colour=True):
        output = {WHITE: {}, BLACK: {}}
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                pos = xy_to_algebraic(x + 1, y + 1)
                if self.is_empty(xy_to_algebraic(x + 1, y + 1)):
                    output[pos] = []
                else:
                    piece = self.get_piece(pos)
                    if piece.colour != self.activeColour and check_colour:
                        output[pos] = []
                    else:
                        output[pos] = self.get_all_valid_moves_from_pos(pos, check_check=check_check)
        return output

    def make_move(self, start_pos, end_pos, check_valid=True, pawn_promotion=QUEEN, update_board_info=True):
        if start_pos == SAN_CASTLE_KINGSIDE:
            self.castle(self.activeColour, KINGSIDE)

        elif start_pos == SAN_CASTLE_QUEENSIDE:
            self.castle(self.activeColour, QUEENSIDE)

        else:
            try:
                target = self.get_piece(start_pos)
            except PieceNotFound:
                raise InvalidMoveError
            if check_valid:
                if self.currentValidMoves == {}:
                    self.currentValidMoves = self.get_all_valid_moves()
                if end_pos not in self.currentValidMoves[target.pos]:
                    raise InvalidMoveError
            self.previousStates.append(self.export_fen())
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
            if end_pos == self.enPassantTarget and target.type == PAWN:
                if target.colour == WHITE:
                    direction = 1
                else:
                    direction = -1
                ep_capture_pos = xy_to_algebraic(target.x, target.y - direction)
                try:
                    ep_capture_target = self.get_piece(ep_capture_pos)
                except PieceNotFound:
                    pass
                else:
                    if ep_capture_target.colour != target.colour:
                        self.capturedPieces.append(ep_capture_target)
                        self.activePieces.remove(ep_capture_target)

            self.enPassantTarget = FEN_EMPTY
            if target.type == PAWN:
                if (target.y == 8 and target.colour == WHITE) or (target.y == 1 and target.colour == BLACK):
                    if pawn_promotion in VALID_PAWN_PROMOTIONS:
                        target.type = pawn_promotion
                    else:
                        raise InvalidMoveError
                else:
                    if target.colour == WHITE:
                        direction = 1
                    else:
                        direction = -1
                    starty = algebraic_to_xy(start_pos)[1]
                    if target.y - starty == direction * 2:
                        self.enPassantTarget = xy_to_algebraic(target.x, target.y - direction)
            # Remove appropriate castling rights if a king or rook is moved.
            elif target.type == KING:
                self.canCastle[target.colour] = {KINGSIDE: False, QUEENSIDE: False}
            elif target.type == ROOK:
                if target.x == 8:
                    self.canCastle[target.colour][KINGSIDE] = False
                elif target.x == 1:
                    self.canCastle[target.colour][QUEENSIDE] = False
            if target.colour == BLACK:
                self.moveClock += 1
            self.activeColour = WHITE if target.colour == BLACK else BLACK
            if update_board_info:
                self.inCheck = self.check_check()
                self.result = self.check_game_outcome()
                self.currentValidMoves = self.get_all_valid_moves()

    def check_check(self):
        for colour in (WHITE, BLACK):
            target_king = None
            for piece in self.activePieces:
                if piece.type == KING and piece.colour == colour:
                    target_king = piece
            if target_king is None:
                break
            for attacker in self.activePieces:
                if attacker.colour != colour:
                    if target_king.pos in self.get_all_valid_moves_from_pos(attacker.pos, check_check=False):
                        return colour
        return None

    def castle(self, colour, direction):
        if self.inCheck == colour:
            raise InvalidMoveError
        elif self.canCastle[colour][direction] is False:
            raise InvalidMoveError
        home_rank = 1 if colour == WHITE else 8
        try:
            target_king = self.get_piece(xy_to_algebraic(5, home_rank))
        except PieceNotFound:
            raise InvalidMoveError
        else:
            if target_king.type != KING or target_king.colour != colour:
                raise InvalidMoveError
        target_rook_file = 8 if direction == KINGSIDE else 1
        direction_multiplier = 1 if direction == KINGSIDE else -1
        try:
            target_rook = self.get_piece(xy_to_algebraic(target_rook_file, home_rank))
        except PieceNotFound:
            raise InvalidMoveError
        else:
            if target_rook.type != ROOK or target_rook.colour != colour:
                raise InvalidMoveError
        for x in range(target_king.x + direction_multiplier, target_rook.x, direction_multiplier):
            if not self.is_empty(xy_to_algebraic(x, home_rank)):
                raise InvalidMoveError
        test_board = Board()
        test_board.load_fen(self.export_fen())
        try:
            current_king_pos = target_king.pos
            for i in range(2):
                new_king_pos = xy_to_algebraic(algebraic_to_xy(current_king_pos)[0] + direction_multiplier, home_rank)
                test_board.make_move(current_king_pos, new_king_pos, check_valid=False)
                if test_board.inCheck == colour:
                    raise InvalidMoveError
                current_king_pos = new_king_pos
        except InvalidMoveError:
            raise InvalidMoveError
        else:
            self.previousStates.append(self.export_fen())
            if direction == KINGSIDE:
                target_king.pos = xy_to_algebraic(7, home_rank)
                target_rook.pos = xy_to_algebraic(6, home_rank)
            elif direction == QUEENSIDE:
                target_king.pos = xy_to_algebraic(3, home_rank)
                target_rook.pos = xy_to_algebraic(4, home_rank)
        target_king.x, target_king.y = algebraic_to_xy(target_king.pos)
        target_rook.x, target_rook.y = algebraic_to_xy(target_rook.pos)
        self.canCastle[colour] = {KINGSIDE: False, QUEENSIDE: False}
        self.enPassantTarget = FEN_EMPTY
        if self.activeColour == BLACK:
            self.moveClock += 1
        self.halfMoveClock += 1
        self.activeColour = BLACK if self.activeColour == WHITE else WHITE
        self.result = self.check_game_outcome()
        self.currentValidMoves = self.get_all_valid_moves()

    def check_game_outcome(self):
        if self.result != IN_PROGRESS:
            return self.result
        if self.halfMoveClock >= 100:  # 100 half moves
            return DRAW  # Draw by 50-move rule
        valid_moves_ignoring_colour = self.get_all_valid_moves(check_colour=False)
        colours = [WHITE, BLACK]
        for colour in colours:
            colour_valid_moves = []
            for piece in self.activePieces:
                if piece.colour == colour:
                    piece_valid_moves = valid_moves_ignoring_colour[piece.pos]
                    if piece_valid_moves:
                        colour_valid_moves.append(piece_valid_moves)

            if len(colour_valid_moves) == 0:
                if self.check_check() is not None:
                    if colour == WHITE:
                        return BLACK_WIN
                    else:
                        return WHITE_WIN
                else:
                    return DRAW
        return IN_PROGRESS
