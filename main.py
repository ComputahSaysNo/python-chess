from game import *
from display import *

def main():
    board = Board()
    print_board_text(board)
    current_player = WHITE
    while True:
        print("It's " + current_player + "'s turn")
        move = str(input("Enter the start position and the end position of the move: ")).lower().split()
        if board.get_piece(move[0]).colour != current_player:
            print("That's not your piece")
            continue
        try:
            board.make_move(move[0],move[1])
            print_board_text(board)
            if current_player == WHITE:
                current_player = BLACK
            else:
                current_player = WHITE
        except InvalidMoveError:
            print("Invalid move, try again")

if __name__ == '__main__':
    main()

