from lib.display import *
import time

class Game():
    def __init__(self):
        pass

def san_to_lan(fen, san):
    """Converts a move in Standard Algebraic Notation (SAN) to a start and end position"""
    backup = san
    if san in (SAN_CASTLE_QUEENSIDE, SAN_CASTLE_KINGSIDE, PGN_CASTLE_QUEENSIDE, PGN_CASTLE_KINGSIDE):
        return san, None
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
            start_rank = char
    possible_start_pieces = []
    for piece in board.activePieces:
        if piece.type == piece_type:
            if board.check_valid_move(piece.pos, end_pos):
                if piece.colour == board.activeColour:
                    possible_start_pieces.append(piece)
    if len(possible_start_pieces) == 1:
        return possible_start_pieces[0].pos, end_pos
    elif len(possible_start_pieces) > 1:
        new_possible_start_pieces = possible_start_pieces
        if start_file is not None:
            for piece in possible_start_pieces:
                if piece.pos[0] != start_file:
                    new_possible_start_pieces.remove(piece)
        if len(new_possible_start_pieces) == 1:
            return new_possible_start_pieces[0].pos, end_pos
        else:
            new_new_possible_start_pieces = new_possible_start_pieces
            if start_rank is not None:
                for piece in new_possible_start_pieces:
                    if algebraic_to_xy(piece.pos)[1] != start_rank:
                        new_new_possible_start_pieces.remove(piece)
        if len(new_new_possible_start_pieces) == 1:
            return possible_start_pieces[0].pos, end_pos
        else:
            raise AmbiguousSAN
    else:
        print(backup)
        raise ValueError

def lan_to_san(fen, start_pos, end_pos, pawn_promotion=QUEEN, check_checkmate=True):
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
        if algebraic_to_xy(end_pos)[1] == 8 and start_piece.colour == WHITE or algebraic_to_xy(end_pos)[
            1] == 1 and start_piece.colour == BLACK:
            promotion = True
    test_board = copy.deepcopy(board)
    test_board.make_move(start_pos, end_pos, check_valid=False)
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