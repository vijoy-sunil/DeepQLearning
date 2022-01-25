import matplotlib.pyplot as plt
import numpy as np
import Game
import Agent

def train():
    # parameters
    episodes = 100
    # id for this training; used in plot figure
    t_id = 0
    # keep track of number of iterations to trigger target model update
    iteration = 0
    # save rewards per episode to plot
    score = []
    agent = Agent.Agent()
    for e in range(0, episodes):
        # clear saved vars before next episode
        epoch, done, reward = 0, False, 0
        env = Game.init_game()
        # get current state
        state = agent.get_state(env)
        # begin an episode
        while not done:
            iteration += 1
            # get actions to execute at current state
            action = agent.get_action(state)
            # execute action, accumulate reward
            next_state, reward, done = agent.play_step(env, action)
            # store in experience replay memory
            experience = state, action, reward, next_state, done
            agent.model.save_replay_memory(experience)
            # update state to next_state
            state = next_state

            # update target model
            # NOTE: from iteration 1 to batch_size, the prediction model
            # is not getting trained as we are collecting experience
            if iteration == agent.model.target_model_update_step:
                print('updating target model weights . . .')
                iteration = 0
                agent.model.update_target_model()
            # train prediction model, NOTE: training starts only after
            # replay memory has minimum batch size
            agent.model.train_model()
            epoch += 1

        # reset game
        Game.reset_game()
        print('episode', e, 'complete, epochs', epoch, 'reward', reward)
        # save reward to plot
        score.append(reward)

    # plot episode vs reward
    plot_result(score, t_id)
    # save model
    agent.model.save_model_weights()
    # close game
    Game.safe_close()

def plot_result(score, t_id):
    n = len(score)
    plt.plot(score, color='r')
    plt.xticks(np.arange(0, n, n-1))
    plt.xlabel('episodes')
    plt.ylabel('reward')
    # save fig to disk
    fig_name = str(t_id) + '.png'
    fig_path = 'Log/' + fig_name
    plt.savefig(fig_path)
    plt.show()

def test():
    pass


if __name__ == '__main__':
    train()
