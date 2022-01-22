import Platformer_Final
import Game_Utils

def main():
    Agent = Platformer_Final.init_game()
    print('Hello World!')
    while True:
        Game_Utils.play_step(Agent)


if __name__ == '__main__':
    main()
