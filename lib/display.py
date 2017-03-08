import pygame
import os
from tkinter import *
from tkinter import filedialog
from lib.game import *


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
    """Converts an algebraic position to the equivalent screen coordinate"""
    file, rank = algebraic_to_xy(pos)
    return (file - 1) * GUI_SQUARE_SIZE + GUI_BOARD_START_POS[0], (BOARD_HEIGHT - rank + 1) * GUI_SQUARE_SIZE


def screen_pos_to_chess_pos(pos):
    """Takes in an (x, y) tuple for the screen position and returns the chess square it's in (or None if it's outside
    the board)"""
    chess_pos = xy_to_algebraic(((pos[0] - GUI_BOARD_START_POS[0]) // GUI_SQUARE_SIZE) + 1,
                                (BOARD_HEIGHT - ((pos[1] - GUI_BOARD_START_POS[1]) // GUI_SQUARE_SIZE)))
    if check_valid_pos(chess_pos):
        return chess_pos
    return None


class ChessGUI:
    """The main class behind the GUI for the chess app. Uses pygame. Has functions for viewing and running a game.
    Most of the graphics are done using the draw method, this must be re-called each time a visual change is made.
    """
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.screen = pygame.display.set_mode([GUI_WIDTH, GUI_HEIGHT], pygame.NOFRAME)
        pygame.display.set_caption(GUI_CAPTION)
        self.clock = pygame.time.Clock()
        self.labelFont = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 4)
        self.buttonFont = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 4)
        self.pieceImages = {WHITE: {}, BLACK: {}}
        self.load_piece_images()
        self.buttons = []
        self.add_menu_buttons()
        self.text = []
        self.draw(START_BOARD, [])

    def new_button(self, x, y, width, height, name, image=None, text=None):
        """Because the different modes have different buttons, this function enables the program to add a new button
        at (x, y). The button can be an image or text. The new button will be drawn each time draw is called"""
        if image is not None:
            self.buttons.append(
                (pygame.transform.scale(pygame.image.load(image), [width, height]), x, y, name, width, height))
        if text is not None:
            width, height = self.buttonFont.size(text)
            self.buttons.append(
                (self.buttonFont.render(text, True, GUI_TEXT_COLOUR), x, y, name, width, height)
            )

    def delete_button(self, name):
        """Removes a button from the list that will be drawn each frame."""
        for button in self.buttons:
            if button[3] == name:
                self.buttons.remove(button)

    def delete_all_buttons(self):
        """Clears all the buttons"""
        self.buttons = []

    def is_click_on_button(self, button_name, click_pos):
        """Takes in an (x, y) tuple for the click position and returns if it is on the button called button_name"""
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

    def add_menu_buttons(self):
        """Adds the most commonly used buttons"""
        self.new_button(0, 0, 0, 0, text="New Game", name="new")
        self.new_button(self.labelFont.size("New game")[0] + 20, 0, 0, 0, text="Open Game", name="open")
        self.new_button(self.labelFont.size("New game")[0] + self.labelFont.size("Open Game")[0] + 40, 0, 0, 0,
                        text="Save Game", name="save")
        self.new_button(self.labelFont.size("New game")[0] + self.labelFont.size("Open Game")[0] + self.labelFont.size(
            "Save Game")[0] + 60, 0, 0, 0, text="Quit", name="quit")

    def load_piece_images(self):
        """Pre-loads the piece images for fast blits when the draw function is called. This only needs to be called
        once at the start of the program"""
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
            pygame.draw.rect(self.screen, colour, [button[1], button[2], button[4] + GUI_SQUARE_SIZE // 10, button[5] + GUI_SQUARE_SIZE // 10])
            self.screen.blit(button[0], (button[1] + GUI_SQUARE_SIZE // 20, button[2] + GUI_SQUARE_SIZE // 20))
        textbox = ScrollingTextBox(self.screen, GUI_SQUARE_SIZE * 10, GUI_SQUARE_SIZE * 15, GUI_SQUARE_SIZE, GUI_SQUARE_SIZE * 9)
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

    def run_game(self, game):
        """Runs a game of chess using a Game class (either generated with the new game dialog or from a pgn). """
        self.delete_all_buttons()
        self.add_menu_buttons()
        self.new_button(chess_pos_to_screen_pos("a1")[0] + 20, chess_pos_to_screen_pos("a1")[1] + GUI_SQUARE_SIZE + 20,
                        0, 0, text="Offer Draw", name="draw")
        self.new_button(chess_pos_to_screen_pos("b1")[0] + 40, chess_pos_to_screen_pos("b1")[1] + GUI_SQUARE_SIZE + 20,
                        0, 0, text="Resign", name="resign")
        self.text = []
        game_info_text = "In game: " + game.pgnTags[PGN_WHITE] + " vs. " + game.pgnTags[PGN_BLACK]
        info_text_width = self.labelFont.size(game_info_text)[0]
        self.text.append((game_info_text, [GUI_SQUARE_SIZE * 10 + (GUI_SQUARE_SIZE * 5 - info_text_width) // 2, GUI_SQUARE_SIZE // 2]))
        whose_turn_text = "White to move" if game.board.activeColour == WHITE else "Black to move"
        self.text.append([whose_turn_text, [GUI_SQUARE_SIZE * 6, GUI_SQUARE_SIZE * 9.25]])
        self.draw(game.board.export_fen())
        selected_pos = None
        highlight = []
        game_running = True
        if game.board.result != IN_PROGRESS:
            game_running = False
        while game_running:
            self.clock.tick(60)
            self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
            for event in pygame.event.get():
                if selected_pos is None:
                    highlight = None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_click_on_button("new", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["new"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        setup = NewGameInfoGUI()
                        data = setup.get_game_setup_params()
                        if data[2]:
                            continue
                        game.new_game(white=data[0], black=data[1])
                        self.run_game(game)
                        return
                    if self.is_click_on_button("quit", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["quit"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        pygame.quit()
                        sys.exit()
                    if self.is_click_on_button("open", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["open"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        root = Tk()
                        root.withdraw()
                        root.overrideredirect(True)
                        root.geometry('0x0+0+0')
                        root.call('wm', 'attributes', '.', '-topmost', True)
                        filename = filedialog.askopenfilename()
                        root.destroy()
                        if filename == "":
                            continue
                        else:
                            try:
                                game = Game()
                                game.load_pgn(filename)
                                self.view_moves(game)
                                return
                            except ValueError:
                                continue
                    if self.is_click_on_button("resign", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["resign"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        if game.board.activeColour == BLACK:
                            game.board.result = WHITE_WIN
                            game.pgnTags[PGN_RESULT] = WHITE_WIN
                            game.moves += WHITE_WIN
                        else:
                            game.board.result = BLACK_WIN
                            game.pgnTags[PGN_RESULT] = BLACK_WIN
                            game.moves += BLACK_WIN
                        game_running = False
                        break
                    if self.is_click_on_button("draw", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["draw"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        choice = None
                        while choice is None:
                            name = "White" if game.board.activeColour == BLACK else "Black"
                            dialog = DrawOfferGUI(name)
                            data = dialog.get_game_setup_params()
                            if data[1]:
                                continue
                            choice = data[0]
                        if choice:
                            game.pgnTags[PGN_RESULT] = DRAW
                            game.board.result = DRAW
                            game.moves += DRAW
                            game_running = False
                            break
                        else:
                            continue
                    if self.is_click_on_button("save", event.pos):
                        self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                  pressed_buttons=["save"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                        root = Tk()
                        root.withdraw()
                        root.overrideredirect(True)
                        root.geometry('0x0+0+0')
                        root.call('wm', 'attributes', '.', '-topmost', True)
                        filename = filedialog.asksaveasfilename()
                        root.destroy()
                        if filename == "":
                            continue
                        else:
                            game.export_pgn(filename)
                    if screen_pos_to_chess_pos(event.pos) == selected_pos:
                        selected_pos = None
                    else:
                        if selected_pos is None:
                            if screen_pos_to_chess_pos(event.pos) is not None:
                                highlight = game.board.get_all_valid_from_pos(screen_pos_to_chess_pos(event.pos))
                                if highlight:
                                    highlight.append(screen_pos_to_chess_pos(event.pos))
                                else:
                                    continue

                                try:
                                    piece = game.board.get_piece(screen_pos_to_chess_pos(event.pos))
                                except PieceNotFound:
                                    pass
                                else:
                                    if piece.colour == game.board.activeColour:
                                        selected_pos = screen_pos_to_chess_pos(event.pos)
                                        if game.board.get_piece(selected_pos).type == KING:
                                            for direction in (KINGSIDE, QUEENSIDE):
                                                home_rank = 1 if game.board.activeColour == WHITE else 8
                                                castle_file = 7 if direction == KINGSIDE else 3
                                                if game.board.is_valid_castle(game.board.activeColour, direction):
                                                    highlight.append(xy_to_algebraic(castle_file, home_rank))
                            else:
                                selected_pos = None
                        else:
                            if screen_pos_to_chess_pos(event.pos) is not None:
                                try:
                                    pawn_promotion = None
                                    if game.board.get_piece(selected_pos).type == KING:
                                        if (selected_pos == "e1" and screen_pos_to_chess_pos(event.pos) == "g1") or (
                                                        selected_pos == "e8" and screen_pos_to_chess_pos(
                                                            event.pos) == "g8"):
                                            selected_pos = SAN_CASTLE_KINGSIDE
                                        elif (selected_pos == "e1" and screen_pos_to_chess_pos(event.pos) == "c1") or (
                                                        selected_pos == "e8" and screen_pos_to_chess_pos(
                                                            event.pos) == "c8"):
                                            selected_pos = SAN_CASTLE_QUEENSIDE
                                    elif game.board.get_piece(selected_pos).type == PAWN:
                                        if (game.board.activeColour == WHITE and
                                                algebraic_to_xy(screen_pos_to_chess_pos(event.pos))[1]) == 8 or (
                                                        game.board.activeColour == BLACK and
                                                        algebraic_to_xy(screen_pos_to_chess_pos(event.pos))[1] == 1):
                                            while pawn_promotion is None:
                                                promotion = SelectPromotion()
                                                pawn_promotion = promotion.get_game_setup_params()
                                except PieceNotFound:
                                    selected_pos = None
                                    continue
                                if game.board.check_valid_move(selected_pos, screen_pos_to_chess_pos(event.pos),
                                                               pawn_promotion=pawn_promotion):
                                    if game.board.activeColour == WHITE:
                                        game.moves += str(game.board.moveClock) + ". "
                                    game.moves += lan_to_san(game.board.export_fen(), selected_pos,
                                                             screen_pos_to_chess_pos(event.pos),
                                                             pawn_promotion=pawn_promotion) + " "
                                    game.board.make_move(selected_pos, screen_pos_to_chess_pos(event.pos),
                                                         pawn_promotion=pawn_promotion)
                                    game.previousBoardStates.append(game.board.export_fen())
                                    game.movesRaw.append(
                                        (selected_pos, screen_pos_to_chess_pos(event.pos)))
                                    if game.board.activeColour == WHITE:
                                        self.text[-1][0] = "White to move"
                                    else:
                                        self.text[-1][0] = "Black to move"
                                    game.board.result = game.board.check_game_outcome()
                                    if game.board.result != IN_PROGRESS:
                                        game.moves += " " + game.board.result
                                        game_running = False

                                    selected_pos = None
                                else:
                                    if game.board.is_empty(screen_pos_to_chess_pos(event.pos)):
                                        highlight = []
                                        selected_pos = None
                                        continue
                                    highlight = game.board.get_all_valid_from_pos(screen_pos_to_chess_pos(event.pos))
                                    if highlight:
                                        highlight.append(screen_pos_to_chess_pos(event.pos))
                                        if game.board.get_piece(screen_pos_to_chess_pos(event.pos)).type == KING:
                                            for direction in (KINGSIDE, QUEENSIDE):
                                                home_rank = 1 if game.board.activeColour == WHITE else 8
                                                castle_file = 7 if direction == KINGSIDE else 3
                                                if game.board.is_valid_castle(game.board.activeColour, direction):
                                                    highlight.append(xy_to_algebraic(castle_file, home_rank))
                                    selected_pos = screen_pos_to_chess_pos(event.pos)
                            else:
                                selected_pos = None
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        win_message = ""
        game.pgnTags[PGN_RESULT] = game.board.result
        if game.board.result == WHITE_WIN:
            win_message = "White wins!"
        elif game.board.result == BLACK_WIN:
            win_message = "Black wins!"
        elif game.board.result == DRAW:
            win_message = "Game is a draw"
        self.text[-1][0] = win_message
        self.draw(game.board.export_fen(), move_text=game.moves)
        self.delete_button("resign")
        self.delete_button("draw")
        self.new_button(chess_pos_to_screen_pos("b1")[0] + 40, chess_pos_to_screen_pos("b1")[1] + GUI_SQUARE_SIZE + 20,
                        0, 0, text="Replay game", name="view")
        self.draw(game.board.export_fen(), move_text=game.moves)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_click_on_button("quit", event.pos):
                        pygame.quit()
                        sys.exit()
                    if self.is_click_on_button("new", event.pos):
                        self.draw(game.board.export_fen(), pressed_buttons=["open"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), move_text=game.moves)
                        setup = NewGameInfoGUI()
                        data = setup.get_game_setup_params()
                        if data[2]:
                            continue
                        game.new_game(white=data[0], black=data[1])
                        self.run_game(game)
                        return
                    if self.is_click_on_button("open", event.pos):
                        self.draw(game.board.export_fen(), pressed_buttons=["open"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), move_text=game.moves)
                        root = Tk()
                        root.withdraw()
                        root.overrideredirect(True)
                        root.geometry('0x0+0+0')
                        root.call('wm', 'attributes', '.', '-topmost', True)
                        filename = filedialog.askopenfilename()
                        root.destroy()
                        if filename == "":
                            continue
                        else:
                            try:
                                game = Game()
                                game.load_pgn(filename)
                                self.view_moves(game)
                                return
                            except ValueError:
                                continue
                    if self.is_click_on_button("view", event.pos):
                        self.draw(game.board.export_fen(), pressed_buttons=["view"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), move_text=game.moves)
                        self.view_moves(game)
                    if self.is_click_on_button("save", event.pos):
                        self.draw(game.board.export_fen(), pressed_buttons=["save"], move_text=game.moves)
                        time.sleep(0.1)
                        self.draw(game.board.export_fen(), move_text=game.moves)
                        root = Tk()
                        root.withdraw()
                        root.overrideredirect(True)
                        root.geometry('0x0+0+0')
                        root.call('wm', 'attributes', '.', '-topmost', True)
                        filename = filedialog.asksaveasfilename()
                        root.destroy()
                        if filename == "":
                            continue
                        else:
                            game.export_pgn(filename)

    def view_moves(self, game):
        """Enables the user to view a previously played game and navigate using buttons/arrow keys. The movetext
        dynamically appears on the right."""
        move_counter = 0
        game_info_text = "Viewing game: " + game.pgnTags[PGN_WHITE] + " vs. " + game.pgnTags[PGN_BLACK] + " (" + \
                         game.pgnTags[PGN_DATE] + ")"
        info_text_width = self.labelFont.size(game_info_text)[0]
        self.text = []
        self.text.append((game_info_text, [GUI_SQUARE_SIZE * 10 + (GUI_SQUARE_SIZE * 5 - info_text_width) // 2, GUI_SQUARE_SIZE // 2]))
        pygame.key.set_repeat(500, 50)
        self.delete_all_buttons()
        self.add_menu_buttons()
        self.new_button(chess_pos_to_screen_pos("e1")[0] + 20, chess_pos_to_screen_pos("e1")[1] + GUI_SQUARE_SIZE + 20,
                        50, 50, "next_move", image="lib/img/buttons/arrow-right.png")
        self.new_button(chess_pos_to_screen_pos("d1")[0] + 20, chess_pos_to_screen_pos("d1")[1] + GUI_SQUARE_SIZE + 20,
                        50, 50, "prev_move", image="lib/img/buttons/arrow-left.png")
        if game.board.result == IN_PROGRESS:
            self.new_button(chess_pos_to_screen_pos("g1")[0] + 20,
                            chess_pos_to_screen_pos("g1")[1] + GUI_SQUARE_SIZE + 20, 0, 0,
                            name="continue_game", text="Continue game")
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
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["new"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          move_text=move_text_up_to_here)
                                setup = NewGameInfoGUI()
                                data = setup.get_game_setup_params()
                                if data[2]:
                                    continue
                                game.new_game(white=data[0], black=data[1])
                                self.run_game(game)
                                return
                            if self.is_click_on_button("open", event.pos):
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["open"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          move_text=move_text_up_to_here)
                                root = Tk()
                                root.withdraw()
                                root.overrideredirect(True)
                                root.geometry('0x0+0+0')
                                root.call('wm', 'attributes', '.', '-topmost', True)
                                filename = filedialog.askopenfilename()
                                root.destroy()
                                if filename == "":
                                    continue
                                else:
                                    try:
                                        game.load_pgn(filename)
                                        self.view_moves(game)
                                        return
                                    except ValueError:
                                        continue
                            if self.is_click_on_button("quit", event.pos):
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["quit"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          move_text=move_text_up_to_here)
                                pygame.quit()
                                sys.exit()
                            if self.is_click_on_button("continue_game", event.pos):
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          pressed_buttons=["continue_game"], move_text=move_text_up_to_here)
                                time.sleep(0.1)
                                self.draw(game.previousBoardStates[move_counter], highlighted_squares=highlight,
                                          move_text=move_text_up_to_here)
                                self.run_game(game)
                            if self.is_click_on_button("save", event.pos):
                                self.draw(game.board.export_fen(), highlighted_squares=highlight,
                                          pressed_buttons=["save"], move_text=game.moves)
                                time.sleep(0.1)
                                self.draw(game.board.export_fen(), highlighted_squares=highlight, move_text=game.moves)
                                root = Tk()
                                root.withdraw()
                                root.overrideredirect(True)
                                root.geometry('0x0+0+0')
                                root.call('wm', 'attributes', '.', '-topmost', True)
                                filename = filedialog.asksaveasfilename()
                                root.destroy()
                                if filename == "":
                                    continue
                                else:
                                    game.export_pgn(filename)


class NewGameInfoGUI:
    """A tkinter dialog that lets the user enter basic info about a new game to be started, to pass on to new_game."""
    def __init__(self):
        self.root = Tk()
        self.root.title("Start New Game")
        self.center_window()
        self.frame = Frame(self.root)
        self.frame.pack()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.cancel = False
        self.player1Name = "white"
        self.player2Name = "black"
        self.instructionMessage = StringVar()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
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

    def close_window(self):
        self.cancel = True
        self.frame.destroy()

    def center_window(self, width=300, height=150):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def ok(self):
        self.player1Name = self.entry_player1Name.get()
        self.player2Name = self.entry_player2Name.get()

        if self.player1Name != "" and self.player2Name != "":
            self.frame.destroy()
        else:
            if self.player1Name == "":
                self.entry_player1Name.insert(ANCHOR, "White")
            if self.player2Name == "":
                self.entry_player2Name.insert(ANCHOR, "Black")

    def get_game_setup_params(self):
        self.root.wait_window(self.frame)  # waits for frame to be destroyed
        self.root.destroy()  # noticed that with "text" gui mode, the tk window stayed...this gets rid of it.
        return self.player1Name, self.player2Name, self.cancel


class DrawOfferGUI:
    """A simple tkinter GUI enabling the player to accept/decline a draw offer"""
    def __init__(self, player_name):
        self.result = None
        self.root = Tk()
        self.root.title("Draw offer made")
        self.center_window()
        self.frame = Frame(self.root)
        self.frame.pack()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.cancel = False
        self.player1Name = "white"
        self.player2Name = "black"
        self.instructionMessage = StringVar()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        Label(self.frame, textvariable=self.instructionMessage).grid(row=0, column=0, columnspan=2)
        self.instructionMessage.set(str(player_name) + ", do you accept the draw offer? ")
        yes = Button(self.frame, text="Yes", command=self.choose_yes)
        yes.grid(row=1, column=0)
        no = Button(self.frame, text="No", command=self.choose_no)
        no.grid(row=1, column=1)

    def close_window(self):
        self.cancel = True
        self.frame.destroy()

    def choose_yes(self):
        self.result = True
        self.frame.destroy()

    def choose_no(self):
        self.result = False
        self.frame.destroy()

    def center_window(self, width=300, height=70):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def get_game_setup_params(self):
        self.root.wait_window(self.frame)  # waits for frame to be destroyed
        self.root.destroy()  # noticed that with "text" gui mode, the tk window stayed...this gets rid of it.
        return self.result, self.cancel


class SelectPromotion:
    """A tkinter GUI that lets the user pick what their pawn will be promoted to"""
    def __init__(self):
        self.root = Tk()
        self.root.title("Select pawn promotion")
        self.center_window()
        self.frame = Frame(self.root)
        self.frame.pack()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.result = None
        self.instructionMessage = StringVar()
        self.root.protocol("WM_DELETE_WINDOW", self.frame.destroy)
        Label(self.frame, textvariable=self.instructionMessage).grid(row=0, columnspan=2)
        self.instructionMessage.set("Choose what the pawn will be promoted to")
        pawn = Button(self.frame, text="Knight", command=self.choose_knight)
        pawn.grid(row=1, column=0)
        pawn = Button(self.frame, text="Rook", command=self.choose_rook)
        pawn.grid(row=1, column=1)
        pawn = Button(self.frame, text="Bishop", command=self.choose_bishop)
        pawn.grid(row=2, column=0)
        pawn = Button(self.frame, text="Queen", command=self.choose_queen)
        pawn.grid(row=2, column=1)

    def center_window(self, width=400, height=80):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def choose_rook(self):
        self.result = ROOK
        self.frame.destroy()

    def choose_bishop(self):
        self.result = BISHOP
        self.frame.destroy()

    def choose_knight(self):
        self.result = KNIGHT
        self.frame.destroy()

    def choose_queen(self):
        self.result = QUEEN
        self.frame.destroy()

    def get_game_setup_params(self):
        self.root.wait_window(self.frame)
        self.root.destroy()
        return self.result


class ScrollingTextBox:
    """A text box, used to display the moves on the side, that scrolls down as more content is added to it."""
    def __init__(self, screen, x_min, x_max, y_min, y_max, bg_colour=GUI_MOVE_TEXT_BOX_COLOUR):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.Font(GUI_FONT_NAME, GUI_SQUARE_SIZE // 5)
        self.bgcolour = bg_colour
        self.xmin = x_min
        self.xmax = x_max
        self.xPixLength = x_max - x_min
        self.ymin = y_min
        self.ymax = y_max
        self.yPixLength = y_max - y_min
        self.lines = []
        (width, height) = self.font.size('A')
        self.lineHeight = height
        self.maxLines = self.yPixLength / self.lineHeight

    def add_line(self, new_line):
        if len(self.lines) + 1 > self.maxLines:
            self.lines.pop(0)
        self.lines.append(new_line)

    def add(self, message):
        (width, height) = self.font.size(message)
        remainder = ""
        if width > self.xPixLength:
            while width > self.xPixLength:
                remainder = message[-1] + remainder
                message = message[0:-1]
                (width, height) = self.font.size(message)

        if len(remainder) > 0:
            if message[-1].isalnum() and remainder[0].isalnum():
                remainder = message[-1] + remainder
                message = message[0:-1] + '-'
                if message[-2] == ' ':
                    message = message[0:-1]

        self.add_line(message)

        if len(remainder) > 0:
            while remainder[0] == ' ':
                remainder = remainder[1:len(remainder)]
            self.add(remainder)

    def draw(self):
        pygame.draw.rect(self.screen, self.bgcolour, [self.xmin, self.ymin, self.xPixLength, self.yPixLength])
        xpos = self.xmin
        ypos = self.ymin
        color = (255, 255, 255)
        for line in self.lines:
            rendered_line = self.font.render(line, True, color)
            self.screen.blit(rendered_line, (xpos, ypos))
            ypos = ypos + self.lineHeight
