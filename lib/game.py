from lib.display import *
import requests
import time

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
