from requests import get
import time
import pygame

WHITE = "white"
BLACK = "black"

# The FEN for the default starting chessboard
START_BOARD = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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

KINGSIDE = "K"
QUEENSIDE = "Q"

VALID_PAWN_PROMOTIONS = (KNIGHT, BISHOP, ROOK, QUEEN)

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

# GUI constants and colours
pygame.init()
GUI_CAPTION = "Chess"
GUI_FONT_NAME = "lib/font/libel-suit-rg.ttf"
GUI_SCREEN_INFO = pygame.display.Info()
GUI_WIDTH = GUI_SCREEN_INFO.current_w
GUI_HEIGHT = GUI_SCREEN_INFO.current_h
GUI_SQUARE_SIZE = 100 * GUI_HEIGHT // 1080
GUI_BOARD_START_POS = (GUI_SQUARE_SIZE, GUI_SQUARE_SIZE)
GUI_FPS = 60
GUI_BG_COLOUR = (49, 46, 43)
GUI_MOVE_TEXT_BOX_COLOUR = (40, 40, 40)
GUI_LIGHT_COLOUR = (238, 238, 210)
GUI_DARK_COLOUR = (118, 150, 86)
GUI_TEXT_COLOUR = (255, 255, 255)
GUI_HIGHLIGHT_COLOUR_1 = (186, 203, 68)
GUI_HIGHLIGHT_COLOUR_2 = (247, 247, 131)
GUI_BUTTON_COLOUR = GUI_DARK_COLOUR
GUI_BUTTON_CLICKED_COLOUR = (123, 183, 55)
HUMAN = 1
COMPUTER = 2
# Info for finding the piece images in the filesystem.
FILENAME_COLOUR = {WHITE: "white", BLACK: "black"}
FILENAME_PIECETYPES = {KING: "king", QUEEN: "queen", ROOK: "rook", BISHOP: "bishop", KNIGHT: "knight", PAWN: "pawn"}

# Display modes
GUI = 1
TEXT = 2

# PGN Parsing
PGN_OPEN_COMMENT = "{"
PGN_CLOSE_COMMENT = "}"
PGN_OPEN_VARIATION = "("
PGN_CLOSE_VARIATION = ")"
PGN_OPEN_TAG = "["
PGN_CLOSE_TAG = "]"
PGN_DEFAULT_EVENT = "Casual Game"
PGN_EVENT = "Event"
PGN_SITE = "Site"
PGN_DATE = "Date"
PGN_ROUND = "Round"
PGN_WHITE = "White"
PGN_BLACK = "Black"
PGN_RESULT = "Result"
PGN_FEN = "FEN"
PGN_CASTLE_KINGSIDE = "0-0"
PGN_CASTLE_QUEENSIDE = "0-0-0"
PGN_MAX_LINE_LENGTH = 80

# Live location and date generation for new games.
freegeoip = "http://freegeoip.net/json"
geo_r = get(freegeoip)
geo_json = geo_r.json()
CURRENT_LOCATION = geo_json["city"] + ", " + geo_json["region_name"] + " " + geo_json["country_code"]
CURRENT_DATE = time.strftime("%Y.%m.%d")
