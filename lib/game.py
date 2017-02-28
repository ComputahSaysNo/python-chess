from lib.board import *
from lib.display import *


class Game:
    def __init__(self):
        self.pgnTags = {PGN_EVENT: None,
                        PGN_SITE: None,
                        PGN_DATE: None,
                        PGN_ROUND: None,
                        PGN_WHITE: None,
                        PGN_BLACK: None,
                        PGN_RESULT: None}
        self.moves = ""
        self.movesRaw = []
        self.previousBoardStates = []
        self.board = Board()

    def new_game(self, event=PGN_DEFAULT_EVENT, site=CURRENT_LOCATION, date=CURRENT_DATE, white="White", black="Black",
                 start_fen=START_BOARD):
        """Resets a Game class based on the PGN parameters passed to it"""
        self.pgnTags[PGN_EVENT] = event
        self.pgnTags[PGN_SITE] = site
        self.pgnTags[PGN_DATE] = date
        self.pgnTags[PGN_WHITE] = white
        self.pgnTags[PGN_BLACK] = black
        if start_fen != START_BOARD:
            self.pgnTags[PGN_FEN] = start_fen
        self.moves = ""
        self.movesRaw = []
        self.previousBoardStates = [start_fen]
        self.board.load_fen(start_fen)

    def load_pgn(self, location):
        """Loads a game from a PGN file (i.e. tags are updated and board is moved)"""
        self.moves = ""
        self.previousBoardStates = [START_BOARD]
        pgn = open(location, "rt")
        lines = []
        for line in pgn:
            lines.append(line.split())
        moves = []
        comment = False
        for line in lines:
            for part in line:
                if not comment:
                    if part[0] == PGN_OPEN_COMMENT:
                        comment = True
                        if part[-1] == PGN_CLOSE_COMMENT:
                            comment = False
                        continue
                    moves.append(part)
                else:
                    if part[-1] == PGN_CLOSE_COMMENT:
                        comment = False
        for move in moves:
            if move in (WHITE_WIN, BLACK_WIN, DRAW):
                self.board.result = move
                self.moves += move
                break
            if move == str(self.board.moveClock) + ".":
                continue
            if move[:len(str(self.board.moveClock)) + 1] == str(self.board.moveClock) + ".":
                move = move[len(str(self.board.moveClock)) + 1:]
            start, end, promotion = san_to_lan(self.board.export_fen(), move)
            prev_fen = self.board.export_fen()
            if self.board.activeColour == WHITE:
                self.moves += str(self.board.moveClock) + ". "
            self.movesRaw.append((start, end))
            self.board.make_move(start, end, pawn_promotion=promotion)
            self.previousBoardStates.append(self.board.export_fen())
            if self.board.check_check(self.board.activeColour):
                check_checkmate = True
            else:
                check_checkmate = False
            self.moves += lan_to_san(prev_fen, start, end, pawn_promotion=promotion,
                                     check_checkmate=check_checkmate) + " "


def san_to_lan(fen, san):
    """Converts a move in Standard Algebraic Notation (SAN) to a start and end position (and a pawn promotion,
    if applicable)"""
    promotion = None
    if san in (SAN_CASTLE_QUEENSIDE, SAN_CASTLE_KINGSIDE, PGN_CASTLE_QUEENSIDE, PGN_CASTLE_KINGSIDE):
        return san, None, promotion
    board = Board()
    board.load_fen(fen)
    for annotation in SAN_ANNOTATIONS:
        if san[-len(annotation):] == annotation:
            san = san[:-len(annotation)]
    if san[-1] == SAN_CHECKMATE:
        san = san[:-1]
    if san[-1] == SAN_CHECK:
        san = san[:-1]
    if san[-len(SAN_EN_PASSANT):] == SAN_EN_PASSANT:
        san = san[:len(SAN_EN_PASSANT)]
    if san[-2] == SAN_PROMOTION:
        promotion = rev_dict(SAN_PIECE_ALIASES)[san[-1]]
        san = san[:-2]
    end_pos = san[-2:]
    san = san[:-2]
    if len(san) >= 1:
        if san[-1] == SAN_CAPTURE:
            san = san[:-1]
    piece_type = PAWN
    if len(san) >= 1:
        if san[0].isupper():
            piece_type = rev_dict(SAN_PIECE_ALIASES)[san[0]]
            san = san[1:]
    start_file = start_rank = None
    for char in san:
        if char.isalpha():
            start_file = char
        elif char.isdigit():
            start_rank = int(char)
    possible_start_pieces = []
    for piece in board.activePieces:
        if piece.type == piece_type:
            if board.check_valid_move(piece.pos, end_pos, pawn_promotion=promotion):
                if piece.colour == board.activeColour:
                    possible_start_pieces.append(piece)
    if len(possible_start_pieces) == 1:
        return possible_start_pieces[0].pos, end_pos, promotion
    elif len(possible_start_pieces) > 1:
        new_possible_start_pieces = possible_start_pieces
        if start_file is not None:
            for piece in possible_start_pieces:
                if piece.pos[0] != start_file:
                    new_possible_start_pieces.remove(piece)
        if len(new_possible_start_pieces) == 1:
            return new_possible_start_pieces[0].pos, end_pos, promotion
        else:
            new_new_possible_start_pieces = new_possible_start_pieces
            if start_rank is not None:
                for piece in new_possible_start_pieces:
                    if algebraic_to_xy(piece.pos)[1] != start_rank:
                        new_new_possible_start_pieces.remove(piece)
        if len(new_new_possible_start_pieces) == 1:
            return possible_start_pieces[0].pos, end_pos, promotion
        else:
            raise AmbiguousSAN
    else:
        raise ValueError


def lan_to_san(fen, start_pos, end_pos, pawn_promotion=None, check_checkmate=True):
    """Converts a start position and end position to standard algebraic notation"""
    board = Board()
    board.load_fen(fen)
    if start_pos in (SAN_CASTLE_KINGSIDE, PGN_CASTLE_KINGSIDE):
        return SAN_CASTLE_KINGSIDE
    if start_pos in (SAN_CASTLE_QUEENSIDE, PGN_CASTLE_QUEENSIDE):
        return SAN_CASTLE_QUEENSIDE
    start_piece = board.get_piece(start_pos)
    start_type = start_piece.type
    en_passant = False
    try:
        board.get_piece(end_pos)
    except PieceNotFound:
        capture = False
        if start_type == PAWN and algebraic_to_xy(end_pos)[0] != algebraic_to_xy(start_pos)[0]:
            capture = True
            en_passant = True
    else:
        capture = True
    promotion = False
    if start_type == PAWN:
        y_pos = algebraic_to_xy(end_pos)[1]
        if y_pos == 8 and start_piece.colour == WHITE or y_pos == 1 and start_piece.colour == BLACK:
            promotion = True
    test_board = copy.deepcopy(board)
    test_board.make_move(start_pos, end_pos, check_valid=False, pawn_promotion=pawn_promotion)
    checkmate = False
    if check_checkmate:
        outcome = test_board.check_game_outcome()
        checkmate = outcome in (WHITE_WIN, BLACK_WIN)
    other_colour = WHITE if start_piece.type == BLACK else BLACK
    if not checkmate and test_board.check_check(other_colour):
        check = True
    else:
        check = False
    ambiguous = []
    for piece in board.activePieces:
        if piece.colour == start_piece.colour and piece.type == start_type and piece.pos != start_pos:
            if board.check_valid_move(piece.pos, end_pos):
                ambiguous.append(piece.pos)
    if ambiguous:
        output = SAN_PIECE_ALIASES[start_type]
        if start_piece.x not in [algebraic_to_xy(i)[0] for i in ambiguous]:
            output += start_pos[0]
        elif start_piece.y not in [algebraic_to_xy(i)[1] for i in ambiguous]:
            output += start_pos[1]
        else:
            output += start_pos
    else:
        output = SAN_PIECE_ALIASES[start_type]
    if capture:
        if start_type == PAWN:
            output = start_pos[0] + SAN_CAPTURE
        else:
            output += SAN_CAPTURE
    output += end_pos
    if promotion:
        output += SAN_PROMOTION + SAN_PIECE_ALIASES[pawn_promotion]
    if en_passant:
        output += SAN_EN_PASSANT
    if check:
        output += SAN_CHECK
    if checkmate:
        output += SAN_CHECKMATE
    return output
