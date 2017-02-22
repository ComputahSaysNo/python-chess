from lib.display import *
import requests
import time


class Game:
    def __init__(self):
        self.tags = {PGN_EVENT: None,
                     PGN_SITE: None,
                     PGN_DATE: None,
                     PGN_ROUND: None,
                     PGN_WHITE: None,
                     PGN_BLACK: None,
                     PGN_RESULT: None}
        self.board = Board()
        self.moves = ""
        self.new_game("Kevin", "Other")
        print(self.tags)

    def new_game(self, white_name, black_name, starting_fen=START_BOARD, event_name=PGN_DEFAULT_EVENT):
        self.tags[PGN_EVENT] = event_name
        freegeoip = "http://freegeoip.net/json"
        geo_r = requests.get(freegeoip)
        geo_json = geo_r.json()
        self.tags[PGN_SITE] = ", ".join([geo_json["city"], geo_json["country_name"]])
        self.tags[PGN_DATE] = time.strftime("%Y.%m.%d")
        self.tags[PGN_ROUND] = "-"
        self.tags[PGN_WHITE] = white_name
        self.tags[PGN_BLACK] = black_name
        self.tags[PGN_RESULT] = IN_PROGRESS
        self.board = Board()
        if starting_fen != START_BOARD:
            self.tags[PGN_FEN] = starting_fen
        self.board.load_fen(starting_fen)

    def run_game(self, display=TEXT):
        if display == TEXT:
            current_player = self.board.activeColour
            waiting_player = BLACK if current_player == WHITE else WHITE
            player_names = {WHITE: self.tags[PGN_WHITE], BLACK: self.tags[PGN_BLACK]}
            game_running = True
            print_board(self.board.export_fen())
            while game_running:
                toggle_player = False
                valid_action_chosen = False
                while not valid_action_chosen:
                    print("")
                    print("It's " + str(player_names[current_player]) + "'s turn")
                    action = str(
                        input("Choose what you want to do [move, see valid, resign, offer draw, save]: ")).lower()
                    if action == "move":
                        valid = False
                        while not valid:
                            print("")
                            move = str(input("Enter the move in algebraic notation: "))
                            if move.lower() == "cancel":
                                break
                            try:
                                start, end = san_to_lan(self.board.export_fen(), move)
                            except AmbiguousSAN:
                                print("Move ambiguous, please enter a starting file/rank")
                                continue
                            except InvalidMoveError:
                                print("Invalid position/not a legal move")
                                continue
                            else:
                                try:
                                    self.board.make_move(start, end)
                                except InvalidMoveError:
                                    print("Invalid move")
                                    continue
                                else:
                                    toggle_player = True
                                    if current_player == WHITE:
                                        self.moves += str(self.board.moveClock) + ". "
                                    self.moves += lan_to_san(self.board.previousStates[-1], start, end) + " "
                                    valid = True
                                    valid_action_chosen = True
                    elif action == "see valid":
                        valid = False
                        while not valid:
                            print("")
                            pos = str(input("Enter the position you'd like to check moves from: ")).lower()
                            if pos == "cancel":
                                break
                            if not check_valid_pos(pos):
                                print("That isn't a valid position")
                                continue
                            if self.board.is_empty(pos):
                                print("There isn't a piece at that position")
                                continue
                            target_piece = self.board.get_piece(pos)
                            valid_moves = self.board.get_all_valid_moves_from_pos(pos)
                            if len(valid_moves) == 0:
                                print("The " + str(target_piece.type) + " at " + str(pos) + " has no legal moves")
                            else:
                                print("The " + str(target_piece.type) + " at " + str(
                                    pos) + " can make the following moves:")
                                for move in valid_moves:
                                    print(lan_to_san(self.board.export_fen(), pos, move))
                            valid = True
                    elif action == "resign":
                        print("Are you sure?")
                        confirm = str(input("Type 'CONFIRM' [all caps] to resign: "))
                        if confirm == "CONFIRM":
                            if self.board.activeColour == WHITE:
                                self.board.result = BLACK_WIN
                                self.moves += " " + BLACK_WIN
                            else:
                                self.board.result = WHITE_WIN
                                self.moves += " " + WHITE_WIN
                            valid_action_chosen = True
                if self.board.result != IN_PROGRESS:
                    game_running = False
                if toggle_player:
                    current_player, waiting_player = waiting_player, current_player
                    print_board(self.board.export_fen())

    def load_pgn(self, location):
        pgn = open(location, "rt")
        lines = []
        for line in pgn:
            lines.append(line.split())
        moves = []
        comment = False
        for line in lines:
            for part in line:
                if not comment:
                    if part[0] == PGN_OPEN_COMMENT:
                        comment = True
                        if part[-1] == PGN_CLOSE_COMMENT:
                            comment = False
                        continue
                    moves.append(part)
                else:
                    if part[-1] == PGN_CLOSE_COMMENT:
                        comment = False
        self.board.load_fen(START_BOARD)
        for move in moves:
            if move in (WHITE_WIN, BLACK_WIN, DRAW):
                self.board.result = move
                break
            if move == str(self.board.moveClock) + ".":
                continue
            if move[:len(str(self.board.moveClock)) + 1] == str(self.board.moveClock) + ".":
                move = move[len(str(self.board.moveClock)) + 1:]
            start, end = san_to_lan(self.board.export_fen(), move)

            self.board.make_move(start, end, check_valid=False, update_board_info=False)
            print_board(self.board.export_fen())



def lan_to_san(fen, start_pos, end_pos, pawn_promotion=QUEEN):
    """Converts a start position and end position to standard algebraic notation"""
    board = Board()
    board.load_fen(fen)
    board.currentValidMoves = board.get_all_valid_moves()
    start_piece = board.get_piece(start_pos)
    start_type = start_piece.type
    en_passant = False
    try:
        board.get_piece(end_pos)
    except PieceNotFound:
        capture = False
        if start_type == PAWN and algebraic_to_xy(end_pos)[0] != algebraic_to_xy(start_pos)[0]:
            capture = True
            en_passant = True
    else:
        capture = True
    promotion = False
    if start_type == PAWN:
        if algebraic_to_xy(end_pos)[1] == 8 and start_piece.colour == WHITE or algebraic_to_xy(end_pos)[
            1] == 1 and start_piece.colour == BLACK:
            promotion = True
    test_board = Board()
    test_board.load_fen(board.export_fen())
    test_board.make_move(start_pos, end_pos, check_valid=False, update_board_info=False)
    if test_board.check_game_outcome() == "1-0" or test_board.check_game_outcome() == "0-1":
        checkmate = True
    else:
        checkmate = False
    other_colour = BLACK if start_piece.colour == WHITE else WHITE
    if not checkmate and test_board.check_check(other_colour) is not None:
        check = True
    else:
        check = False
    ambiguous = []
    for piece in board.activePieces:
        if piece.colour == start_piece.colour and piece.type == start_type and piece.pos != start_pos:
            if end_pos in board.currentValidMoves[piece.pos]:
                ambiguous.append(piece.pos)
    if ambiguous:
        output = SAN_PIECE_ALIASES[start_type]
        if start_piece.x not in [algebraic_to_xy(i)[0] for i in ambiguous]:
            output += start_pos[0]
        elif start_piece.y not in [algebraic_to_xy(i)[1] for i in ambiguous]:
            output += start_pos[1]
        else:
            output += start_pos
    else:
        output = SAN_PIECE_ALIASES[start_type]
    if capture:
        if start_type == PAWN:
            output = start_pos[0] + SAN_CAPTURE
        else:
            output += SAN_CAPTURE
    output += end_pos
    if promotion:
        output += SAN_PROMOTION + SAN_PIECE_ALIASES[pawn_promotion]
    if en_passant:
        output += SAN_EN_PASSANT
    if check:
        output += SAN_CHECK
    if checkmate:
        output += SAN_CHECKMATE
    return output


def san_to_lan(fen, san):
    """Converts a move in Standard Algebraic Notation (SAN) to a start and end position"""
    print(san)
    backup = san
    if san == SAN_CASTLE_KINGSIDE or san == SAN_CASTLE_QUEENSIDE:
        return san, None
    board = Board()
    board.load_fen(fen)
    board.currentValidMoves = board.get_all_valid_moves()
    for annotation in SAN_ANNOTATIONS:
        if san[-len(annotation):] == annotation:
            san = san[:-len(annotation)]
    if san[-1] == SAN_CHECKMATE:
        san = san[:-1]
    if san[-1] == SAN_CHECK:
        san = san[:-1]
    if san[-len(SAN_EN_PASSANT):] == SAN_EN_PASSANT:
        san = san[:len(SAN_EN_PASSANT)]
    if san[-2] == SAN_PROMOTION:
        san = san[:-2]
    end_pos = san[-2:]
    san = san[:-2]
    if len(san) >= 1:
        if san[-1] == SAN_CAPTURE:
            san = san[:-1]
    piece_type = PAWN
    if len(san) >= 1:
        if san[0].isupper():
            piece_type = rev_dict(SAN_PIECE_ALIASES)[san[0]]
            san = san[1:]
    start_file = start_rank = None
    for char in san:
        if char.isalpha():
            start_file = char
        elif char.isdigit():
            start_rank = char
    possible_start_pieces = []
    for piece in board.activePieces:
        if piece.type == piece_type:
            if end_pos in board.currentValidMoves[piece.pos]:
                if piece.colour == board.activeColour:
                    possible_start_pieces.append(piece)
    if len(possible_start_pieces) == 1:
        return possible_start_pieces[0].pos, end_pos
    elif len(possible_start_pieces) > 1:
        new_possible_start_pieces = possible_start_pieces
        if start_file is not None:
            for piece in possible_start_pieces:
                if piece.pos[0] != start_file:
                    new_possible_start_pieces.remove(piece)
        if len(new_possible_start_pieces) == 1:
            return new_possible_start_pieces[0].pos, end_pos
        else:
            new_new_possible_start_pieces = new_possible_start_pieces
            if start_rank is not None:
                for piece in new_possible_start_pieces:
                    if algebraic_to_xy(piece.pos)[1] != start_rank:
                        new_new_possible_start_pieces.remove(piece)
        if len(new_new_possible_start_pieces) == 1:
            return possible_start_pieces[0].pos, end_pos
        else:
            raise AmbiguousSAN
    else:
        print(backup)
        raise InvalidMoveError
