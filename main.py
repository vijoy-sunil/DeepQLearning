import Platformer_Final
import Game_Utils
import pygame

# parameters
episodes = 10

def main():
    print('Hello World!')
    for e in range(0, episodes):
        # clear saved vars before next episode
        epoch, done, reward = 0, False, 0
        Agent = Platformer_Final.init_game()

        # get current state
        state = Game_Utils.get_state(Agent)

        # set actions to execute at current state
        # [sh jump, ln jump, left, right]
        actions = [0, 1, 0, 0]

        while not done:
            next_state, reward, done = Game_Utils.play_step(Agent, actions)
            epoch += 1

        # reset game
        Game_Utils.reset_game()
        print('episode', e, 'complete, epochs', epoch, 'reward', reward)

    # close game
    Game_Utils.safe_close()


if __name__ == '__main__':
    main()
