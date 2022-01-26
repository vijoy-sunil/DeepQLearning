import random
import numpy as np
# The model type that we will be using is Sequential. Sequential
# is the easiest way to build a model in Keras. It allows you to
# build a model layer by layer. Each layer has weights that correspond
# to the layer the follows it.
from keras.models import Sequential
from keras.models import load_model
from keras.optimizers import adam_v2
from keras.layers import Dense
from collections import deque

class DQNModel:
    def __init__(self):
        self.learning_rate = 0.0005
        # loss function, that is used to estimate the loss of the model
        # so that the weights can be updated to reduce the loss on the
        # next evaluation
        # The Mean Squared Error, or MSE, loss is the default loss to use
        # for regression problems. Use Mean Squared Error when you desire
        # to have large errors penalized more than smaller ones.
        self.loss = 'mse'
        # Keras Adam Optimizer is the most popular and widely used optimizer
        # for neural network training.
        self.optimizer = adam_v2.Adam(learning_rate=self.learning_rate)
        # Replay memory to store experiences of the model with the
        # environment, implemented as A double-ended queue, or deque, which
        # has the feature of adding and removing elements from either end.
        self.replay_memory_size = 25000
        self.replay_memory = deque(maxlen=self.replay_memory_size)
        # The batch size is a number of samples processed before the model is
        # updated
        self.batch_size = 1000
        # file name and path to save model. Model weights are saved to HDF5
        # format. This is a grid format that is ideal for storing multidime-
        # -nsional arrays of numbers.
        self.weights_file_name = 'Weights/QNetwork_'
        # update target model after this many epochs
        self.target_model_update_step = 100
        # get state size and action size from agent
        self.state_size = 12
        self.action_size = 4
        # discount factor for future rewards
        self.gamma = 0.7
        # prediction and target model
        self.pred_model = self.create_model()
        self.target_model = self.create_model()

    # construct the deep model; same model for pred and target
    def create_model(self):
        model = Sequential()
        # define model layers
        model.add(Dense(256, activation='relu', input_shape=(self.state_size,)))
        model.add(Dense(self.action_size, activation='linear'))
        # Compile defines the loss function, the optimizer and the metrics.
        # It has nothing to do with the weights, and you can compile a model
        # as many times as you want without causing any problem to pretrained
        # weights. You need a compiled model to train (because training uses
        # the loss function and the optimizer).
        model.compile(loss=self.loss, optimizer=self.optimizer)

        # Keras provides a way to summarize a model.
        # The summary is textual and includes information about:
        #
        # The layers and their order in the model.
        # The output shape of each layer.
        # The number of parameters (weights) in each layer.
        # The total number of parameters (weights) in the model.
        model.summary()
        return model

    # after some time interval update the target model to be same
    # with the prediction model
    def update_target_model(self):
        self.target_model.set_weights(self.pred_model.get_weights())

    # load and save model weights, NOTE: we are not saving model
    # architecture here
    def load_model_weights(self, t_id):
        weights_file = self.weights_file_name + str(t_id) + '.h5'
        weights = load_model(weights_file)
        return weights

    def save_model_weights(self, t_id):
        weights_file = self.weights_file_name + str(t_id) + '.h5'
        self.pred_model.save(weights_file)

    # save to experience replay memory
    def save_replay_memory(self, experience):
        self.replay_memory.append(experience)

    # train model
    def train_model(self):
        # experience replay as part of training process
        # randomly sample a batch from deque replay memory
        if len(self.replay_memory) > self.batch_size:
            mini_batch = random.sample(self.replay_memory, self.batch_size)
        else:
            return

        # unravel mini batch
        states = []
        next_states = []
        for index, sample in enumerate(mini_batch):
            state, action, reward, next_state, done = sample
            states.append(state)
            next_states.append(next_state)

        states = np.array(states)
        next_states = np.array(next_states)

        # batch prediction
        # predict q value for state using pred_model
        predicted_q = self.pred_model.predict(states)
        # predict q value for next state using target_model
        target_q = self.target_model.predict(next_states)

        for index, sample in enumerate(mini_batch):
            state, action, reward, next_state, done = sample
            if not done:
                # close the gap between target_q and predicted_q
                predicted_q[index][action] = reward + self.gamma * np.argmax(target_q[index])
            else:
                predicted_q[index][action] = reward

        # train with this batch
        # with states as input, tune the weights such that they
        # are close to predicted_q
        self.pred_model.fit(states, predicted_q, batch_size=self.batch_size, verbose=0)
