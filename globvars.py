# Colour IDs (for board squares and pieces)
WHITE = 1001
BLACK = 1002
COLOUR_NAMES = {WHITE:"White",BLACK:"Black"}

# Piece IDs
EMPTY = 2000
PAWN = 2001
KNIGHT = 2002
BISHOP = 2003
ROOK = 2004
QUEEN = 2005
KING = 2006

PIECE_NAMES_SHORT = {"P": PAWN, "N": KNIGHT, "B": BISHOP, "R": ROOK, "Q": QUEEN, "K": KING}
PIECE_NAMES = {PAWN: "Pawn", KNIGHT: "Knight", BISHOP: "Bishop", ROOK: "Rook", QUEEN: "Queen", KING: "King"}

# Board info

# Bad things will probably happen if you set either of these greater than 26
BOARD_WIDTH = 8
BOARD_HEIGHT = 8

STARTING_BOARD = "Ra1 Nb1 Bc1 Qd1 Ke1 Bf1 Ng1 Rh1 Pa2 Pb2 Pc2 Pd2 Pe2 Pf2 Pg2 Ph2 " \
                 "pa7 pb7 pc7 pd7 pe7 pf7 pg7 ph7 ra8 nb8 bc8 qd8 ke8 bf8 ng8 rh8"

# Other useful things
ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
