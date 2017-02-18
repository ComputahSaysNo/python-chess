from lib.game import *


def test():
    print(run_pgn("lib/test_pgn/test.pgn"))


def main():
    board = Board()
    board.load_fen(START_BOARD)
    current_player = board.activeColour
    if current_player == WHITE:
        waiting_player = BLACK
    else:
        waiting_player = WHITE
    print_board(board.export_fen())
    while True:
        toggle_player = False
        print("It's " + str(current_player) + "'s turn")
        move = str(input("Enter the move: "))
        if move == "fen":
            print(board.export_fen())
        elif move == "pass":
            toggle_player = True
        elif move == SAN_CASTLE_KINGSIDE:
            try:
                board.castle(current_player, KINGSIDE)
            except InvalidMoveError:
                print("Invalid castle")
            else:
                toggle_player = True
        elif move == SAN_CASTLE_QUEENSIDE:
            try:
                board.castle(current_player, QUEENSIDE)
            except InvalidMoveError:
                print("Invalid castle")
            else:
                toggle_player = True
        else:
            try:
                start, end = san_to_lan(board.export_fen(), move)
            except AmbiguousSAN:
                print("Ambiguous SAN, specify rank/file of start piece")
            else:
                if board.get_piece(start).colour != current_player:
                    print("That isn't your piece")
                    continue
                try:
                    board.make_move(start, end)
                except InvalidMoveError:
                    print("Invalid Move")
                    continue
                except ValueError:
                    print("Invalid position/No piece can legally move there")
                    continue
                else:
                    toggle_player = True
            # move = move.split()
            # for part in move:
            #     if not check_valid_pos(part):
            #         print("Invalid position[s]")
            #         continue
            # try:
            #     target = board.get_piece(move[0])
            # except PieceNotFound:
            #     print("There isn't a piece at that position")
            #     continue
            # if target.colour != current_player:
            #     print("That is not your piece")
            #     continue
            # if len(move) == 1:
            #     valid_moves = board.get_all_valid_moves_from_pos(move[0])
            #     if len(valid_moves) != 0:
            #         print("The " + str(target.type) + " at " + move[0] + " can make these moves: ")
            #         for i in valid_moves:
            #             print(i)
            #     else:
            #         print("The " + str(target.type) + " at " + move[0] + " has no legal moves")
            # elif len(move) == 2:
            #     promotion = ""
            #     if target.type == PAWN:
            #         if (algebraic_to_xy(move[1])[1] == 8 and target.colour == WHITE) or (
            #                 algebraic_to_xy(move[1])[1] == 1 and target.colour == BLACK):
            #             while True:
            #                 print("Pawn promotion detected, what should it be promoted to?")
            #                 promotion = str(input("Choose from: N (knight), B (bishop), R (rook), Q (queen)  ")).upper()
            #                 if promotion not in FEN_PIECE_ALIASES:
            #                     print("Invalid promotion, try again")
            #                     continue
            #                 if FEN_PIECE_ALIASES[promotion] not in (KNIGHT, BISHOP, ROOK, QUEEN):
            #                     print("Invalid promotion, try again")
            #                     continue
            #                 promotion = FEN_PIECE_ALIASES[promotion]
            #                 break
            #     print(promotion)
            #     try:
            #         board.make_move(move[0], move[1], update_board_info=True, pawn_promotion=promotion)
            #     except InvalidMoveError:
            #         print("Invalid move")
            #     else:
            #         toggle_player = True
            #         print(lan_to_san(board.previousStates[-1],move[0],move[1],pawn_promotion=promotion))

        if toggle_player:
            print_board(board.export_fen())
            bucket = current_player
            current_player = waiting_player
            waiting_player = bucket
            if board.check_game_outcome() != IN_PROGRESS:
                break
    print(board.export_fen())
    print(board.result)


if __name__ == '__main__':
    test()
