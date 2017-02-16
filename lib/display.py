import os

import pygame

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


class GUIPiece(pygame.sprite.Sprite):
    def __init__(self, file, rank, piece_type, colour):
        pygame.sprite.Sprite.__init__(self)
        self.colour = colour
        self.type = piece_type
        self.file, self.rank = file, rank
        self.pos = xy_to_algebraic(file, rank)
        img_location = "lib/img/pieces/" + FILENAME_COLOUR[self.colour] + "/" + FILENAME_PIECETYPES[self.type] + ".png"
        self.image = pygame.transform.scale(pygame.image.load(img_location), [GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])
        self.rect = self.image.get_rect()
        self.rect.center = (GUI_BOARD_START_POS[0] + (file - 0.5) * GUI_SQUARE_SIZE,
                            GUI_BOARD_START_POS[1] + (BOARD_HEIGHT - rank + 0.5) * GUI_SQUARE_SIZE)




class ChessGUI:
    def __init__(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption(GUI_CAPTION)
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.screen = pygame.display.set_mode(GUI_DIMENSIONS)
        pygame.Surface.fill(self.screen, GUI_BG_COLOUR)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 5)
        self.start_x, self.start_y = GUI_BOARD_START_POS
        self.pieceSprites = pygame.sprite.Group()
        self.draw_board()
        self.load_pieces(START_BOARD)
        pygame.display.update()
        self.mainloop()

    def draw_board(self):
        for y in range(BOARD_HEIGHT):
            y_pos = self.start_y + GUI_SQUARE_SIZE * y
            for x in range(BOARD_WIDTH):
                x_pos = self.start_x + GUI_SQUARE_SIZE * x
                colour = GUI_LIGHT_COLOUR if (x + y) % 2 == 0 else GUI_DARK_COLOUR
                pygame.draw.rect(self.screen, colour, [x_pos, y_pos, GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])
        pygame.draw.rect(self.screen, (0, 0, 0),
                         [self.start_x, self.start_y, GUI_SQUARE_SIZE * 8, GUI_SQUARE_SIZE * 8], GUI_SQUARE_SIZE // 20)
        x_pos = self.start_x + GUI_SQUARE_SIZE // 2
        y_pos = self.start_y - GUI_SQUARE_SIZE // 2
        for i in range(BOARD_WIDTH):
            x_label = self.font.render(ALPHABET[i], True, GUI_TEXT_COLOUR)
            self.screen.blit(x_label, [x_pos, y_pos])
            x_pos += GUI_SQUARE_SIZE
        x_pos = self.start_x - GUI_SQUARE_SIZE // 2
        y_pos = self.start_y + GUI_SQUARE_SIZE // 2
        for i in range(BOARD_HEIGHT, 0, -1):
            y_label = self.font.render(str(i), True, GUI_TEXT_COLOUR)
            self.screen.blit(y_label, [x_pos, y_pos])
            y_pos += GUI_SQUARE_SIZE
        pygame.display.update()

    def load_pieces(self, fen):
        board = fen.split()[0]
        ranks = board.split("/")
        rank_counter = 8
        for rank in ranks:
            file_counter = 1
            for char in rank:
                if char.isdigit():
                    file_counter += int(char)
                else:
                    colour = WHITE if char.isupper() else BLACK
                    self.pieceSprites.add(
                        (GUIPiece(file_counter, rank_counter, FEN_PIECE_ALIASES[char.upper()], colour)))
                    file_counter += 1
            rank_counter -= 1
        self.pieceSprites.draw(self.screen)

    def get_click_pos(self, click_event):
        x, y = click_event.pos
        x = x - self.start_x
        y = y - self.start_y
        result = ((x // GUI_SQUARE_SIZE) + 1, BOARD_HEIGHT - (y // GUI_SQUARE_SIZE))
        if 0 < result[0] <= BOARD_WIDTH and 0 < result[1] <= BOARD_HEIGHT:
            return xy_to_algebraic(result[0], result[1])
        else:
            return None

    def get_piece(self, pos):
        for piece in self.pieceSprites:
            if piece.pos == pos:
                return piece
        return None

    def move_piece(self, start_pos, end_pos):
        piece = self.get_piece(start_pos)

    def mainloop(self):
        while True:
            self.clock.tick(GUI_FPS)
            for e in pygame.event.get():
                if e.type is pygame.KEYDOWN:
                    if e.key is pygame.K_ESCAPE:
                        pygame.quit()
                        return
                if e.type is pygame.QUIT:
                    pygame.quit()
                    return
                if e.type is pygame.MOUSEBUTTONDOWN:
                    print(self.get_click_pos(e))
