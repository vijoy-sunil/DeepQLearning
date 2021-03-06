import matplotlib.pyplot as plt
import numpy as np
import Agent

def train(t_id):
    # train episodes
    episodes = 2500
    # keep track of number of episodes to trigger target model update
    ep_iteration = 0
    # save weights after checkpoint
    ep_checkpoint = 100
    # save rewards per episode, moving avg to plot
    all_rewards = []
    moving_avg = []

    agent = Agent.Agent()
    for e in range(0, episodes):
        # clear saved vars before next episode
        epoch, done, reward = 0, False, 0
        exploration, exploitation = 0, 0
        # get current state
        state = agent.get_state()
        # begin an episode
        ep_iteration += 1
        while not done:
            # get actions to execute at current state
            egr, action = agent.get_action(state)
            # debug purposes, see how many of the actions in this
            # episode are exploration vs exploitation
            if egr == 0:
                exploration += 1
            else:
                exploitation += 1
            # execute action, get reward for executing action
            next_state, score, done = agent.play_step(action)
            # store in experience replay memory
            experience = state, action, score, next_state, done
            agent.model.save_replay_memory(experience)
            # update state to next_state
            state = next_state
            # cumulative reward
            reward += score

            # update target model
            if ep_iteration == agent.model.target_model_update_episode:
                print('updating target model weights . . .')
                ep_iteration = 0
                agent.model.update_target_model()
                print('done')
            # train prediction model, NOTE: training starts only after
            # replay memory has minimum batch size
            agent.model.train_model()
            epoch += 1

        # reset game
        agent.safe_reset()
        print('episode', e, 'complete, epochs', epoch, 'reward', reward,
              'exploration', exploration, 'exploitation', exploitation)
        # save weights as checkpoint
        if e % ep_checkpoint == 0:
            checkpoint_id = '_' + str(e)
            agent.model.save_model_weights(t_id, checkpoint_id)
        # save reward, moving avg to plot
        all_rewards.append(reward)
        moving_avg.append(sum(all_rewards)/len(all_rewards))

    # end of training
    print('training complete')
    # plot episode vs reward
    plot_result(all_rewards, moving_avg, t_id)
    # save final model
    checkpoint_id = '_' + str(episodes - 1)
    agent.model.save_model_weights(t_id, checkpoint_id)
    # close game
    Agent.safe_close()

def plot_result(score, moving_avg, t_id):
    n = len(score)
    plt.plot(score, color='g')
    # moving average
    plt.plot(moving_avg, color='r')

    plt.xticks(np.arange(0, n, n-1))
    plt.xlabel('episodes')
    plt.ylabel('reward')
    # save fig to disk
    fig_name = str(t_id) + '.png'
    fig_path = 'Log/' + fig_name
    plt.savefig(fig_path)
    plt.show()


if __name__ == '__main__':
    # t_id - training id; used in figures, weights saved
    train(0)
