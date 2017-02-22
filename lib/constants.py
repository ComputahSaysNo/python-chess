WHITE = "white"
BLACK = "black"

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

KING = "king"
QUEEN = "queen"
ROOK = "rook"
BISHOP = "bishop"
KNIGHT = "knight"
PAWN = "pawn"

# SAN Parsing
SAN_PIECE_ALIASES = {KING: "K", QUEEN: "Q", ROOK: "R", BISHOP: "B", KNIGHT: "N", PAWN: ""}
SAN_CHECK = "+"
SAN_CHECKMATE = "#"
SAN_PROMOTION = "="
SAN_CAPTURE = "x"
SAN_ANNOTATIONS = ["!!", "!", "!?", "?!", "?", "??", "", "+/-", "+/=", "=", "=/+", "-/+"]
SAN_EN_PASSANT = "e.p."
SAN_CASTLE_QUEENSIDE = "O-O-O"
SAN_CASTLE_KINGSIDE = "O-O"


BOARD_WIDTH = BOARD_HEIGHT = 8

START_BOARD = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

KINGSIDE = "K"
QUEENSIDE = "Q"

VALID_PAWN_PROMOTIONS = [KNIGHT, BISHOP, ROOK, QUEEN]

# FEN Parsing:
FEN_PIECE_ALIASES = {"K": KING, "Q": QUEEN, "R": ROOK, "B": BISHOP, "N": KNIGHT, "P": PAWN}
FEN_COLOUR_ALIASES = {"W": WHITE, "B": BLACK}
FEN_CASTLING_ALIASES = {"K": KINGSIDE, "Q": QUEENSIDE}
FEN_EMPTY = "-"

# Game results
WHITE_WIN = "1-0"
BLACK_WIN = "0-1"
DRAW = "1/2-1/2"
IN_PROGRESS = "*"

GUI_DIMENSIONS = (1600, 1000)
GUI_CAPTION = "Chess"
GUI_FONT_NAME = "lib/font/Aquatico-Regular.otf"
GUI_BOARD_START_POS = (100, 100)
GUI_SQUARE_SIZE = 100  # pixels
GUI_FPS = 144

GUI_BG_COLOUR = (49, 46, 43)
GUI_LIGHT_COLOUR = (254, 206, 157)
GUI_DARK_COLOUR = (209, 139, 69)
GUI_TEXT_COLOUR = (255, 255, 255)
GUI_HIGHLIGHT_COLOUR = (66, 155, 244)

FILENAME_COLOUR = {WHITE: "white", BLACK: "black"}
FILENAME_PIECETYPES = {KING: "king", QUEEN: "queen", ROOK: "rook", BISHOP: "bishop", KNIGHT: "knight", PAWN: "pawn"}

GUI = 1
TEXT = 2

PGN_OPEN_COMMENT = "{"
PGN_CLOSE_COMMENT = "}"
PGN_OPEN_VARIATION = "("
PGN_CLOSE_VARIATION = ")"
PGN_DEFAULT_EVENT = "Casual Game"
PGN_EVENT = "Event"
PGN_SITE = "Site"
PGN_DATE = "Date"
PGN_ROUND = "Round"
PGN_WHITE = "White"
PGN_BLACK = "Black"
PGN_RESULT = "Result"
PGN_FEN = "FEN"