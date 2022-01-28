import Agent
import numpy as np
import Train

def test(t_id):
    # test episodes
    episodes = 10
    # save rewards per episode, moving avg to plot
    all_rewards = []
    moving_avg = []

    agent = Agent.Agent()
    # load model weights
    agent.model.target_model = agent.model.load_model_weights(t_id)

    for e in range(0, episodes):
        # clear saved vars before next episode
        epoch, done, reward = 0, False, 0
        # get current state
        state = agent.get_state()
        # begin an episode
        while not done:
            # get actions to execute at current state, using target model
            state = state.reshape(1, agent.state_size)
            action = np.argmax(agent.model.target_model.predict(state))
            # execute action, get reward for executing the action
            next_state, score, done = agent.play_step(action)
            # update state to next_state
            state = next_state
            reward += score
            epoch += 1

        # reset game
        agent.safe_reset()
        print('episode', e, 'complete, epochs', epoch, 'reward', reward)
        # save reward, moving avg to plot
        all_rewards.append(reward)
        moving_avg.append(sum(all_rewards)/len(all_rewards))

    # end of training
    print('testing complete, max reward', max(all_rewards), 'min reward', min(all_rewards))
    # plot episode vs reward
    # append t_id to mark this as a test run
    t_id = t_id + 0.1
    Train.plot_result(all_rewards, moving_avg, t_id)
    # close game
    Agent.safe_close()


if __name__ == '__main__':
    # t_id - testing id; used in figures, loading weights
    test(2)
