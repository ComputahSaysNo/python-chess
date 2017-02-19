import os

# import pygame

from lib.board import *


def print_board(fen):
    x_header = "   a  b  c  d  e  f  g  h"
    board = fen.split()[0]
    ranks = board.split("/")
    output = [x_header]
    rank_counter = 8
    for rank in ranks:
        new_row = str(rank_counter) + " "
        for char in rank:
            if char.isdigit():
                for i in range(int(char)):
                    new_row += "[ ]"
            else:
                new_row += "[" + char + "]"
        new_row += " " + str(rank_counter)
        output.append(new_row)
        rank_counter -= 1
    output.append(x_header)
    for i in output:
        print(i)


# def chess_pos_to_screen_pos(pos):
#     file, rank = algebraic_to_xy(pos)
#     return (file - 1) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0], (BOARD_HEIGHT - rank + 1) * GUI_SQUARE_SIZE
#
#
# class ChessGUI:
#     def __init__(self):
#         os.environ["SDL_VIDEO_CENTERED"] = "1"
#         pygame.init()
#         self.screen = pygame.display.set_mode(GUI_DIMENSIONS)
#         pygame.display.set_caption(GUI_CAPTION)
#         self.clock = pygame.time.Clock()
#         self.font = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 5)
#         self.pieceImages = {WHITE: {}, BLACK: {}}
#         self.load_piece_images()
#         self.draw_board(START_BOARD, [])
#         while True:
#             for e in pygame.event.get():
#                 if e.type is pygame.QUIT:
#                     pygame.quit()
#                     return
#
#     def load_piece_images(self):
#         for colour in (WHITE, BLACK):
#             for piece in (KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN):
#                 img_path = "lib/img/pieces/" + FILENAME_COLOUR[colour] + "/" + FILENAME_PIECETYPES[piece] + ".png"
#                 self.pieceImages[colour][piece] = pygame.transform.scale(pygame.image.load(img_path),
#                                                                          [GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])
#
#     def draw_board(self, fen, highlighted_squares=None):
#         # Step 1: Draw background and board
#         pygame.Surface.fill(self.screen, GUI_BG_COLOUR)
#         for y in range(BOARD_HEIGHT):
#             y_pos = GUI_BOARD_START_POS[1] + GUI_SQUARE_SIZE * y
#             for x in range(BOARD_WIDTH):
#                 x_pos = GUI_BOARD_START_POS[0] + GUI_SQUARE_SIZE * x
#                 colour = GUI_LIGHT_COLOUR if (x + y) % 2 == 0 else GUI_DARK_COLOUR
#                 pygame.draw.rect(self.screen, colour, [x_pos, y_pos, GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])
#         pygame.draw.rect(self.screen, (0, 0, 0),
#                          [GUI_BOARD_START_POS[0], GUI_BOARD_START_POS[1], GUI_SQUARE_SIZE * 8, GUI_SQUARE_SIZE * 8],
#                          GUI_SQUARE_SIZE // 20)
#         # Step 2: Draw board labels
#         x_pos = GUI_BOARD_START_POS[0] + GUI_SQUARE_SIZE // 2
#         y_pos = GUI_BOARD_START_POS[1] - GUI_SQUARE_SIZE // 2
#         for i in range(BOARD_WIDTH):
#             x_label = self.font.render(ALPHABET[i], True, GUI_TEXT_COLOUR)
#             self.screen.blit(x_label, [x_pos, y_pos])
#             x_pos += GUI_SQUARE_SIZE
#         x_pos = GUI_BOARD_START_POS[0] - GUI_SQUARE_SIZE // 2
#         y_pos = GUI_BOARD_START_POS[1] + GUI_SQUARE_SIZE // 2
#         for i in range(BOARD_HEIGHT, 0, -1):
#             y_label = self.font.render(str(i), True, GUI_TEXT_COLOUR)
#             self.screen.blit(y_label, [x_pos, y_pos])
#             y_pos += GUI_SQUARE_SIZE
#         # Step 3: Blit piece images to screen
#         board = fen.split()[0]
#         ranks = board.split("/")
#         rank_counter = 8
#         for rank in ranks:
#             file_counter = 1
#             for char in rank:
#                 if char.isdigit():
#                     file_counter += int(char)
#                 else:
#                     colour = WHITE if char.isupper() else BLACK
#                     piece_type = FEN_PIECE_ALIASES[char.upper()]
#                     draw_pos = [(file_counter - 1) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0],
#                                 (BOARD_HEIGHT - rank_counter) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0]]
#                     self.screen.blit(self.pieceImages[colour][piece_type], draw_pos)
#                     file_counter += 1
#             rank_counter -= 1
#         # Step 4: Apply square highlights.
#         if highlighted_squares is not None:
#             for square in highlighted_squares:
#                 x, y = chess_pos_to_screen_pos(square)
#                 pygame.draw.rect(self.screen, GUI_HIGHLIGHT_COLOUR, [x, y, GUI_SQUARE_SIZE, GUI_SQUARE_SIZE],
#                                  GUI_SQUARE_SIZE // 20)
#         pygame.display.flip()
