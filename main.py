from game import *

def toggle_player(player):
    if player == WHITE:
        return BLACK
    else:
        return WHITE

def main():
    run_game_text()

if __name__ == '__main__':
    main()
