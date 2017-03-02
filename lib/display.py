import pygame
import os
from tkinter import *
from lib.game import *

class TkinterGameSetupParams:
    def __init__(self):
        self.root = Tk()
        self.root.title("Start New Game")
        self.center_window()
        self.frame = Frame(self.root)
        self.frame.pack()
        self.root.call('wm', 'attributes', '.', '-topmost', True)

        self.instructionMessage = StringVar()
        Label(self.frame, textvariable=self.instructionMessage).grid(row=0)
        self.instructionMessage.set("Please enter game options. ")

        Label(self.frame, text="Name").grid(row=1, column=1)

        Label(self.frame, text="Player 1 (White)").grid(row=2, column=0)
        self.entry_player1Name = Entry(self.frame)
        self.entry_player1Name.grid(row=2, column=1)
        self.entry_player1Name.insert(ANCHOR, "White")

        Label(self.frame, text="Player 2 (Black)").grid(row=3, column=0)
        self.entry_player2Name = Entry(self.frame)
        self.entry_player2Name.grid(row=3, column=1)
        self.entry_player2Name.insert(ANCHOR, "Black")

        b = Button(self.frame, text="Start", command=self.ok)
        b.grid(row=4, column=1)

    def center_window(self, width=800, height=150):
        # get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def ok(self):
        self.player1Name = self.entry_player1Name.get()
        self.player2Name = self.entry_player2Name.get()

        if self.player1Name != "" and self.player2Name != "":
            self.frame.destroy()
        else:
            # self.instructionMessage.set("Please input a name for both players!")
            if self.player1Name == "":
                self.entry_player1Name.insert(ANCHOR, "White")
            if self.player2Name == "":
                self.entry_player2Name.insert(ANCHOR, "Black")

    def GetGameSetupParams(self):
        self.root.wait_window(self.frame)  # waits for frame to be destroyed
        self.root.destroy()  # noticed that with "text" gui mode, the tk window stayed...this gets rid of it.
        return (self.player1Name, self.player2Name)


def print_board(fen):
    """Prints a board in text format based on a FEN"""
    x_header = "   " + "  ".join([ALPHABET[i] for i in range(BOARD_WIDTH)])
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


def chess_pos_to_screen_pos(pos):
    file, rank = algebraic_to_xy(pos)
    return (file - 1) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0], (BOARD_HEIGHT - rank + 1) * GUI_SQUARE_SIZE


def screen_pos_to_chess_pos(pos):
    chess_pos = xy_to_algebraic(((pos[0] - GUI_BOARD_START_POS[0]) // GUI_SQUARE_SIZE) + 1,
                                (BOARD_HEIGHT - ((pos[1] - GUI_BOARD_START_POS[1]) // GUI_SQUARE_SIZE)))
    if check_valid_pos(chess_pos):
        return chess_pos
    return None


class ScrollingTextBox:
    def __init__(self, screen, xmin, xmax, ymin, ymax, bgcolour=GUI_MOVE_TEXT_BOX_COLOUR):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 5)
        self.bgcolour = bgcolour
        self.xmin = xmin
        self.xmax = xmax
        self.xPixLength = xmax - xmin
        self.ymin = ymin
        self.ymax = ymax
        self.yPixLength = ymax - ymin
        self.lines = []
        (width, height) = self.font.size('A')
        self.lineHeight = height
        self.maxLines = self.yPixLength / self.lineHeight

    def add_line(self, new_line):
        # outside functions shouldn't call this...call Add instead (appropriately breaks up message string into lines)
        # there can only be "self.maxLines" in the self.lines array
        #  if textbox is not full, just append the newLine
        #  if textbox is full, pop a line off from the front and add newLine to the back
        if len(self.lines) + 1 > self.maxLines:
            self.lines.pop(0)  # pop(0) pops off beginning; pop() pops off end
        self.lines.append(new_line)

    def add(self, message):
        # Break up message string into multiple lines, if necessary
        (width, height) = self.font.size(message)
        remainder = ""
        if width > self.xPixLength:
            while width > self.xPixLength:
                remainder = message[-1] + remainder
                message = message[0:-1]  # chop off last character
                (width, height) = self.font.size(message)

        if len(remainder) > 0:
            if message[-1].isalnum() and remainder[0].isalnum():
                remainder = message[-1] + remainder
                message = message[0:-1] + '-'
                if message[-2] == ' ':
                    message = message[0:-1]  # remove the '-'

        self.add_line(message)

        if len(remainder) > 0:
            # remove leading spaces
            while remainder[0] == ' ':
                remainder = remainder[1:len(remainder)]
            self.add(remainder)

    def draw(self):
        # Draw all lines
        pygame.draw.rect(self.screen, self.bgcolour, [self.xmin, self.ymin, self.xPixLength, self.yPixLength])
        xpos = self.xmin
        ypos = self.ymin
        color = (255, 255, 255)  # white
        antialias = 1  # evidently, for some people rendering text fails when antialiasing is off
        for line in self.lines:
            rendered_line = self.font.render(line, antialias, color)
            self.screen.blit(rendered_line, (xpos, ypos))
            ypos = ypos + self.lineHeight


class ChessGUI:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.screen = pygame.display.set_mode(GUI_DIMENSIONS)
        pygame.display.set_caption(GUI_CAPTION)
        self.clock = pygame.time.Clock()
        self.labelFont = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 4)
        self.buttonFont = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 4)
        self.pieceImages = {WHITE: {}, BLACK: {}}
        self.load_piece_images()
        self.buttons = []
        self.text = []
        self.draw(START_BOARD, [])

    def new_button(self, x, y, width, height, name, image=None, text=None):
        if image is not None:
            self.buttons.append(
                (pygame.transform.scale(pygame.image.load(image), [width, height]), x, y, name, width, height))
        if text is not None:
            width, height = self.buttonFont.size(text)
            self.buttons.append(
                (self.buttonFont.render(text, True, GUI_TEXT_COLOUR), x, y, name, width, height)
            )

    def delete_button(self, name):
        for button in self.buttons:
            if button[3] == name:
                self.buttons.remove(button)

    def delete_all_buttons(self):
        self.buttons = []

    def is_click_on_button(self, button_name, click_pos):
        target = None
        for button in self.buttons:
            if button[3] == button_name:
                target = button
        if target is None:
            return False
        x, y = click_pos[0], click_pos[1]
        if target[1] <= x <= target[1] + target[4]:
            if target[2] <= y <= target[2] + target[5]:
                return True
        return False

    def load_piece_images(self):
        for colour in (WHITE, BLACK):
            for piece in (KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN):
                img_path = "lib/img/pieces/" + FILENAME_COLOUR[colour] + "/" + FILENAME_PIECETYPES[piece] + ".png"
                self.pieceImages[colour][piece] = pygame.transform.scale(pygame.image.load(img_path),
                                                                         [GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])

    def draw(self, fen, highlighted_squares=None, pressed_buttons=None, move_text=""):
        # Step 1: Draw background and board
        pygame.Surface.fill(self.screen, GUI_BG_COLOUR)
        for y in range(BOARD_HEIGHT):
            y_pos = GUI_BOARD_START_POS[1] + GUI_SQUARE_SIZE * y
            for x in range(BOARD_WIDTH):
                x_pos = GUI_BOARD_START_POS[0] + GUI_SQUARE_SIZE * x
                colour = GUI_LIGHT_COLOUR if (x + y) % 2 == 0 else GUI_DARK_COLOUR
                if highlighted_squares is not None:
                    if xy_to_algebraic(x + 1, 8 - y) in highlighted_squares:
                        colour = GUI_HIGHLIGHT_COLOUR_1 if colour == GUI_DARK_COLOUR else GUI_HIGHLIGHT_COLOUR_2
                pygame.draw.rect(self.screen, colour, [x_pos, y_pos, GUI_SQUARE_SIZE, GUI_SQUARE_SIZE])
        pygame.draw.rect(self.screen, (0, 0, 0),
                         [GUI_BOARD_START_POS[0], GUI_BOARD_START_POS[1], GUI_SQUARE_SIZE * 8, GUI_SQUARE_SIZE * 8],
                         GUI_SQUARE_SIZE // 20)
        # Step 2: Draw board labels
        x_pos = GUI_BOARD_START_POS[0] + GUI_SQUARE_SIZE // 2
        y_pos = GUI_BOARD_START_POS[1] - GUI_SQUARE_SIZE // 2
        for i in range(BOARD_WIDTH):
            x_label = self.labelFont.render(ALPHABET[i], True, GUI_TEXT_COLOUR)
            self.screen.blit(x_label, [x_pos, y_pos])
            x_pos += GUI_SQUARE_SIZE
        x_pos = GUI_BOARD_START_POS[0] - GUI_SQUARE_SIZE // 2
        y_pos = GUI_BOARD_START_POS[1] + GUI_SQUARE_SIZE // 2
        for i in range(BOARD_HEIGHT, 0, -1):
            y_label = self.labelFont.render(str(i), True, GUI_TEXT_COLOUR)
            self.screen.blit(y_label, [x_pos, y_pos])
            y_pos += GUI_SQUARE_SIZE
        # Step 3: Blit piece images to screen
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
                    piece_type = FEN_PIECE_ALIASES[char.upper()]
                    draw_pos = [(file_counter - 1) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0],
                                (BOARD_HEIGHT - rank_counter) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0]]
                    self.screen.blit(self.pieceImages[colour][piece_type], draw_pos)
                    file_counter += 1
            rank_counter -= 1
        for button in self.buttons:
            colour = GUI_BUTTON_COLOUR
            if pressed_buttons is not None:
                if button[3] in pressed_buttons:
                    colour = GUI_BUTTON_CLICKED_COLOUR
            pygame.draw.rect(self.screen, colour, [button[1], button[2], button[4] + 10, button[5] + 10])
            self.screen.blit(button[0], (button[1] + 5, button[2] + 5))
        textbox = ScrollingTextBox(self.screen, 1000, 1500, 100, 900)
        move_text = move_text.split(" ")
        for part in move_text:
            if len(part) >= 2:
                if part[0].isdigit() and part[-1] == ".":
                    text_to_add = part
                    try:
                        counter = move_text.index(part) + 1
                        while not (move_text[counter][0].isdigit() and move_text[counter][-1] == "."):
                            text_to_add += " " + move_text[counter]
                            counter += 1
                    except IndexError:
                        pass
                    textbox.add(text_to_add)
        textbox.draw()
        for part in self.text:
            to_blit = self.labelFont.render(part[0], True, GUI_TEXT_COLOUR)
            self.screen.blit(to_blit, part[1])
        pygame.display.flip()

    def add_menu_buttons(self):
        self.new_button(0, 0, 0, 0, text="New Game", name="new")
        self.new_button(self.labelFont.size("New game")[0] + 20, 0, 0, 0, text="Open Game", name="open")
        self.new_button(self.labelFont.size("New game")[0] + self.labelFont.size("Open Game")[0] + 40, 0, 0, 0,
                        text="Save Game", name="save")

    def run_game(self, game):
        self.delete_all_buttons()
        self.add_menu_buttons()
        self.new_button(chess_pos_to_screen_pos("a1")[0] + 20, chess_pos_to_screen_pos("a1")[1] + GUI_SQUARE_SIZE + 20,
                        0, 0, text="Offer Draw", name="draw")
        self.new_button(chess_pos_to_screen_pos("b1")[0] + 40, chess_pos_to_screen_pos("b1")[1] + GUI_SQUARE_SIZE + 20,
                        0, 0, text="Resign", name="resign")
        self.text = []
        game_info_text = "In game: " + game.pgnTags[PGN_WHITE] + " vs. " + game.pgnTags[PGN_BLACK]
        info_text_width = self.labelFont.size(game_info_text)[0]
        self.text.append((game_info_text, [1000 + (500 - info_text_width) // 2, 60]))
        self.text.append(["White to move", [600, 925]])
        self.draw(game.board.export_fen())
        selected_pos = None
        highlight = []
        game_running = True
        while game_running:
            self.clock.tick(60)
            self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
            for e in pygame.event.get():
                if selected_pos == None:
                    highlight = None
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if screen_pos_to_chess_pos(e.pos) == selected_pos:
                        selected_pos = None
                    else:
                        if selected_pos is None:
                            if screen_pos_to_chess_pos(e.pos) is not None:
                                highlight = game.board.get_all_valid_from_pos(screen_pos_to_chess_pos(e.pos))
                                highlight.append(screen_pos_to_chess_pos(e.pos))
                                selected_pos = screen_pos_to_chess_pos(e.pos)
                            else:
                                selected_pos = None
                        else:
                            if screen_pos_to_chess_pos(e.pos) is not None:
                                try:
                                    if game.board.get_piece(selected_pos).type == KING:
                                        if (selected_pos == "e1" and screen_pos_to_chess_pos(e.pos) == "g1") or (selected_pos == "e8" and screen_pos_to_chess_pos(e.pos) == "g8"):
                                            selected_pos = SAN_CASTLE_KINGSIDE
                                        elif (selected_pos == "e1" and screen_pos_to_chess_pos(e.pos) == "c1") or (selected_pos == "e8" and screen_pos_to_chess_pos(e.pos) == "c8"):
                                            selected_pos = SAN_CASTLE_QUEENSIDE
                                        pass
                                except PieceNotFound:
                                    selected_pos = None
                                    continue
                                if game.board.check_valid_move(selected_pos, screen_pos_to_chess_pos(e.pos), pawn_promotion=QUEEN):
                                    if game.board.activeColour == WHITE:
                                        game.moves += str(game.board.moveClock) + ". "
                                    game.moves += lan_to_san(game.board.export_fen(), selected_pos, screen_pos_to_chess_pos(e.pos), pawn_promotion=QUEEN) + " "
                                    game.board.make_move(selected_pos, screen_pos_to_chess_pos(e.pos), pawn_promotion=QUEEN)
                                    if game.board.activeColour == WHITE:
                                        self.text[-1][0] = "White to move"
                                    else:
                                        self.text[-1][0] = "Black to move"
                                    game.board.result = game.board.check_game_outcome()
                                    if game.board.result != IN_PROGRESS:
                                        game.moves += " " + game.board.result
                                        self.draw(game.board.export_fen(), move_text=game.moves)
                                        print(game.moves)
                                        game_running = False

                                    selected_pos = None
                                else:
                                    highlight = game.board.get_all_valid_from_pos(screen_pos_to_chess_pos(e.pos))
                                    highlight.append(screen_pos_to_chess_pos(e.pos))
                                    selected_pos = screen_pos_to_chess_pos(e.pos)
                            else:
                                selected_pos = None
                elif e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def view_moves(self, game):
        move_counter = 0
        game_info_text = "Viewing game: " + game.pgnTags[PGN_WHITE] + " vs. " + game.pgnTags[PGN_BLACK] + " (" + \
                         game.pgnTags[PGN_DATE] + ")"
        info_text_width = self.labelFont.size(game_info_text)[0]
        self.text.append((game_info_text, [1000 + (500 - info_text_width) // 2, 60]))
        pygame.key.set_repeat(500, 50)
        self.delete_all_buttons()
        self.add_menu_buttons()
        self.new_button(chess_pos_to_screen_pos("e1")[0] + 20, chess_pos_to_screen_pos("e1")[1] + GUI_SQUARE_SIZE + 20,
                        50, 50, "next_move", image="lib/img/buttons/arrow-right.png")
        self.new_button(chess_pos_to_screen_pos("d1")[0] + 20, chess_pos_to_screen_pos("d1")[1] + GUI_SQUARE_SIZE + 20,
                        50, 50, "prev_move", image="lib/img/buttons/arrow-left.png")
        while True:
            last_move_start = None
            last_move_end = None
            if move_counter > 0:
                last_move_start = game.movesRaw[move_counter - 1][0]
                last_move_end = game.movesRaw[move_counter - 1][1]
            if last_move_start in (
                    PGN_CASTLE_KINGSIDE, PGN_CASTLE_QUEENSIDE, SAN_CASTLE_KINGSIDE, SAN_CASTLE_QUEENSIDE):
                king_start_file = 5
                if FEN_COLOUR_ALIASES[game.previousBoardStates[move_counter - 1].split(" ")[1].upper()] == WHITE:
                    home_rank = 1
                else:
                    home_rank = 8
                if last_move_start in (PGN_CASTLE_KINGSIDE, SAN_CASTLE_KINGSIDE):
                    king_end_file = 7
                else:
                    king_end_file = 3
                last_move_start = xy_to_algebraic(king_start_file, home_rank)
                last_move_end = xy_to_algebraic(king_end_file, home_rank)

            highlight = [last_move_start, last_move_end] if last_move_start is not None else []
            moves_copy = game.moves.split()
            if move_counter == len(game.movesRaw):
                move_text_up_to_here = game.moves
            else:
                for part in moves_copy:
                    if part[-1] == "." and part[0:-1] == game.previousBoardStates[move_counter].split()[5]:
                        whose_turn = 1 if game.previousBoardStates[move_counter].split()[1] == "w" else 2
                        move_text_up_to_here = " ".join(moves_copy[:moves_copy.index(part) + whose_turn])
                        if move_text_up_to_here.split()[-1][-1] == "." and move_text_up_to_here.split()[-1][
                                                                           0:-1].isdigit():
                            move_text_up_to_here = " ".join(move_text_up_to_here.split()[:-1])
            self.draw(game.previousBoardStates[move_counter], highlight, move_text=move_text_up_to_here)
            next_move = False
            while not next_move:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT:
                            next_move = True
                            if move_counter < len(game.previousBoardStates) - 1:
                                move_counter += 1
                        if event.key == pygame.K_LEFT:
                            next_move = True
                            if move_counter > 0:
                                move_counter -= 1
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if self.is_click_on_button("next_move", event.pos):
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["next_move"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                next_move = True
                                if move_counter < len(game.previousBoardStates) - 1:
                                    move_counter += 1
                            if self.is_click_on_button("prev_move", event.pos):
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["prev_move"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                next_move = True
                                if move_counter > 0:
                                    move_counter -= 1
                            if self.is_click_on_button("new", event.pos):
                                setup = TkinterGameSetupParams()
                                data = setup.GetGameSetupParams()
                                game.new_game(white=data[0], black=data[1])
                                self.run_game(game)
                                return
