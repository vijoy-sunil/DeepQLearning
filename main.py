import Game
import Agent

# parameters
episodes = 10

def main():
    agent = Agent.Agent()
    for e in range(0, episodes):
        # clear saved vars before next episode
        epoch, done, reward = 0, False, 0
        env = Game.init_game()

        # get current state
        state = agent.get_state(env)

        # get actions to execute at current state
        # [sh jump + none,
        #  sh jump + left,
        #  sh jump + right,
        #  ln jump + none,
        #  ln jump + left,
        #  ln jump + right,
        #  left,
        #  right,
        #  none]
        actions = [0, 1, 0, 0, 0, 0, 0, 0, 0]

        while not done:
            next_state, reward, done = agent.play_step(env, actions)
            epoch += 1

        # reset game
        Game.reset_game()
        print('episode', e, 'complete, epochs', epoch, 'reward', reward)

    # close game
    Game.safe_close()


if __name__ == '__main__':
    main()
