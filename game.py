from board import *
from display import *


def run_game_text():
    player1 = "White"  # str(input("Player 1 name: "))
    player2 = "Black"  # str(input("Player 2 name: "))
    player_to_colour = {player1: WHITE, player2: BLACK}
    running = True
    game_board = Board(BOARD_WIDTH, BOARD_HEIGHT, STARTING_BOARD)
    current_player = player1
    waiting_player = player2
    print("On each turn, type the start and end position of a move (e.g. e2 e4) to make that move, type a position to"
          " get all valid moves from that position, type castle kingside or castle queenside to castle, \n"
          "type pass to pass the turn to the other player, or type resign"
          " to withdraw from the game")
    print_board_text(game_board)
    while running:
        print("It's " + current_player + "'s turn")
        toggle_players = False  # If this is set to true during the move, swap the players at the end of the loop
        move = str(input("Enter the move: ")).lower()
        if move == "resign":
            print(current_player + " resigns, " + waiting_player + " wins!")
            running = False
        elif move == "pass":
            print("Passing to " + waiting_player)
            toggle_players = True
        elif move == "castle kingside":
            try:
                game_board.castle(player_to_colour[current_player], KINGSIDE)
            except InvalidMoveError:
                print("Invalid castle")
            else:
                toggle_players = True
        elif move == "castle queenside":
            try:
                game_board.castle(player_to_colour[current_player], QUEENSIDE)
            except InvalidMoveError:
                print("Invalid castle")
            else:
                toggle_players = True
        else:
            move = move.split()
            for part in move:
                try:
                    pos = algebraic_to_xy(part)
                    for dim in pos:
                        if dim > game_board.dimensions[0] - 1:
                            print("Position outside of board, try again")
                            move = []
                            continue
                except ValueError:
                    print("Invalid input, try again")
                    move = []
                    continue
            if len(move) == 2:
                try:
                    game_board.make_move(move[0], move[1], player_to_colour[current_player])
                except InvalidMoveError:
                    print("Invalid move, try again")
                else:
                    toggle_players = True
            elif len(move) == 1:
                try:
                    moves = game_board.get_all_piece_moves(move[0])
                except PieceNotFound:
                    print("There isn't a piece at " + move[0])
                else:
                    if len(moves) == 0:
                        print("The " + PIECE_NAMES_LONG[game_board.get_piece(move[0]).type] + " at " +
                              move[0] + " has no legal moves")
                    else:
                        print("The " + PIECE_NAMES_LONG[game_board.get_piece(move[0]).type] + " at " +
                              move[0] + " can make these moves: ")
                        for move in moves:
                            print(move)
        if toggle_players:
            print_board_text(game_board)
            bucket = current_player
            current_player = waiting_player
            waiting_player = bucket
            if game_board.check_checkmate(player_to_colour[current_player]):
                print(waiting_player + " wins!")
                running = False
            elif game_board.check_check(player_to_colour[current_player]):
                print(current_player + " is in check")
        print("")
