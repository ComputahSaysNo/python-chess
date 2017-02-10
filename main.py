from display import *
from board import *


def main():
    board = Board(BOARD_WIDTH, BOARD_HEIGHT, STARTING_BOARD)
    print_board_text(board)
    current_player = WHITE
    while True:
        print("It's " + current_player + "'s turn")
        move = str(input("Enter the start position and the end position of the move: ")).lower().split()
        if move == ["pass"]:
            if current_player == WHITE:
                current_player = BLACK
            else:
                current_player = WHITE
            continue
        try:
            board.get_piece(move[0])
        except PieceNotFound:
            print("Piece not found")
            continue
        if len(move) == 1:
            print(board.get_all_valid_moves(move[0]))
            continue
        try:
            board.make_move(move[0], move[1], current_player)
            print_board_text(board)
            if current_player == WHITE:
                current_player = BLACK
            else:
                current_player = WHITE
        except InvalidMoveError:
            print("Invalid move, try again")
        if board.check_checkmate(current_player):
            print(current_player + " has  been checkmated!")
            break
        if board.check_check(current_player):
            print(current_player + " is in check")


if __name__ == '__main__':
    main()
