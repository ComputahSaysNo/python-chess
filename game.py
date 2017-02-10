from board import *

class Game:

    def __init__(self):
        self.game_board = Board(BOARD_WIDTH, BOARD_HEIGHT, STARTING_BOARD)
        self.players = ()