from lib.display import *

if __name__ == '__main__':
    game = Game()
    game.new_game()
    display = ChessGUI()
    setup = NewGameInfoGUI()
    data = setup.get_game_setup_params()
    if data[2]:
        pygame.quit()
        sys.exit()
    game.new_game(white=data[0], black=data[1])
    display.run_game(game)