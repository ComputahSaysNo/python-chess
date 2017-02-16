from lib.board import *
from lib.constants import *
from lib.display import *
from lib.game import *
from lib.exceptions import *

def main():
    board = Board()
    board.load_fen(START_BOARD)
    current_player = WHITE
    waiting_player = BLACK
    print_board(board.export_fen())
    while True:
        toggle_player = False
        print("It's " + str(current_player) + "'s turn")
        move = str(input("Enter the move: ")).lower()
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
            move = move.split()
            for part in move:
                if not check_valid_pos(part):
                    print("Invalid position[s]")
                    continue
            try:
                target = board.get_piece(move[0])
            except PieceNotFound:
                print("There isn't a piece at that position")
                continue
            if target.colour != current_player:
                print("That is not your piece")
                continue
            if len(move) == 1:
                valid_moves = board.get_all_valid_moves_from_pos(move[0])
                if len(valid_moves) != 0:
                    print("The " + str(target.type) + " at " + move[0] + " can make these moves: ")
                    for i in valid_moves:
                        print(i)
                else:
                    print("The " + str(target.type) + " at " + move[0] + " has no legal moves")
            elif len(move) == 2:
                try:
                    board.make_move(move[0], move[1])
                except InvalidMoveError:
                    print("Invalid move")
                else:
                    toggle_player = True

        if toggle_player:
            bucket = current_player
            current_player = waiting_player
            waiting_player = bucket
            print_board(board.export_fen())
            if board.check_game_outcome() != IN_PROGRESS:
                break
        print(board.moves)
        print(board.export_fen())
    print(board.moves)
    print(board.export_fen())
    print(board.result)


if __name__ == '__main__':
    main()
