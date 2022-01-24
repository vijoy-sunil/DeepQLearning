import Game
import Agent

# parameters
episodes = 10

def train():
    # keep track of number of iterations to trigger target model
    # update
    iteration = 0
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
            # action = agent.get_action(state)
            action = 3
            # execute action, accumulate reward
            next_state, reward, done = agent.play_step(env, action)
            # store in experience replay memory
            experience = state, action, reward, next_state, done
            agent.model.save_replay_memory(experience)
            # update state to next_state
            state = next_state

            if done:
                # save best model
                pass

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

    # close game
    Game.safe_close()


if __name__ == '__main__':
    train()
