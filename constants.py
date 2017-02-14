WHITE = "white"
BLACK = "black"

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

KING = "king"
QUEEN = "queen"
ROOK = "rook"
BISHOP = "bishop"
KNIGHT = "knight"
PAWN = "pawn"
SAN_PIECE_ALIASES = {KING: "K", QUEEN: "Q", ROOK: "R", BISHOP: "B", KNIGHT: "N", PAWN: " "}

BOARD_WIDTH = BOARD_HEIGHT = 8

START_BOARD = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

KINGSIDE = "K"
QUEENSIDE = "Q"

# FEN Parsing:
FEN_PIECE_ALIASES = {"K": KING, "Q": QUEEN, "R": ROOK, "B": BISHOP, "N": KNIGHT, "P": PAWN}
FEN_COLOUR_ALIASES = {"W": WHITE, "B": BLACK}
FEN_CASTLING_ALIASES = {"K": KINGSIDE, "Q": QUEENSIDE}
FEN_EMPTY_EPTARGET = "-"
