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

BOARD_DIMENSIONS = (8, 8)
STARTING_BOARD = "Ra1 Nb1 Bc1 Qd1 Ke1 Bf1 Ng1 Rh1 Pa2 Pb2 Pc2 Pd2 Pe2 Pf2 Pg2 Ph2 nb3 " \
                 "pa7 pb7 pc7 pd7 pe7 pf7 pg7 ph7 ra8 nb8 bc8 qd8 ke8 bf8 ng8 rh8"
PIECE_LOADING_ALIASES = {"K": KING, "Q": QUEEN, "R": ROOK, "B": BISHOP, "N": KNIGHT, "P": PAWN}
