# Colour IDs (for board squares and pieces)
WHITE = "White"
BLACK = "Black"

# Piece info
PAWN = "P"
KNIGHT = "N"
BISHOP = "B"
ROOK = "R"
QUEEN = "Q"
KING = "K"
PIECE_NAMES_LONG = {PAWN: "Pawn", KNIGHT: "Knight", BISHOP: "Bishop", ROOK: "Rook", QUEEN: "Queen", KING: "King"}

# Board info
BOARD_WIDTH = 8
BOARD_HEIGHT = 8
STARTING_BOARD = "Ra1 Nb1 Bc1 Qd1 Ke1 Bf1 Ng1 Rh1 Pa2 Pb2 Pc2 Pd2 Pe2 Pf2 Pg2 Ph2 " \
                 "pa7 pb7 pc7 pd7 pe7 pf7 pg7 ph7 ra8 nb8 bc8 qd8 ke8 bf8 ng8 rh8"

# Display
TEXT_GUI_PADDING = "[ ]"



DISPLAY_PIECES = {
    WHITE: {KING: "K", QUEEN: "Q", ROOK: "R", BISHOP: "B", KNIGHT: "N", PAWN: "P"},
    BLACK: {KING: "k", QUEEN: "q", ROOK: "r", BISHOP: "b", KNIGHT: "n", PAWN: "p"}
}

# Other useful things
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

KINGSIDE = 0
QUEENSIDE = 1