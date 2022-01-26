import Game
import pygame
from pygame.locals import *
from collections import Iterable
import sys
import random
import numpy as np
import Model

FramePerSec = pygame.time.Clock()

# sort platform list based on y coordinate
def sort_rule(e):
    return e[1]

class Agent:
    def __init__(self):
        # reward (not included in Game file)
        self.game_over_reward = -25
        # constants
        self.epsilon = 0.8
        # [Player.x, Player.y,
        #  Platform1.x, Platform1.y,
        #  Platform2.x, Platform2.y,
        #  Platform3.x, Platform3.y,
        #  Platform4.x, Platform4,y,
        #  Coin1.x, Coin1.y,
        #  Velocity.y]
        self.state_size = 13
        # [sh jump + none,      0
        #  sh jump + left,      1
        #  sh jump + right,     2
        #  ln jump + none,      3
        #  ln jump + left,      4
        #  ln jump + right,     5
        #  left,                6
        #  right,               7
        #  none]                8
        self.action_size = 9
        # deep network
        self.model = Model.DQNModel()

    # get current state
    def get_state(self, P1):
        pl_above = []
        pl_below = []
        pl_coin = []
        # filter platforms
        for p_entity in Game.platforms:
            p_y = p_entity.rect.centery
            # Check if platform is visible
            if p_y < 0:
                continue
            # save platforms above the player
            if p_y < P1.pos[1]:
                pl_above.append(p_entity.rect.center)
            # save platforms below the player
            elif P1.pos[1] < p_y < Game.HEIGHT:
                pl_below.append(p_entity.rect.center)
            # save platforms with coin; above player
            if p_y < P1.pos[1] and p_entity.isCoin:
                pl_coin.append(p_entity.rect.center)

        # sort platforms lowest to highest y
        pl_above.sort(key=sort_rule)
        pl_below.sort(key=sort_rule)
        pl_coin.sort(key=sort_rule)

        # if no platforms above
        if len(pl_above) == 0:
            pl_above = [[Game.WIDTH/2, 0]]
        # if no platforms below
        if len(pl_below) == 0:
            pl_below = [[Game.WIDTH/2, Game.HEIGHT]]

        # pick and choose what features/observations to use
        nearest_below = pl_below[0]
        nearest_above = pl_above[-1]
        middle_above_idx = int(len(pl_above) / 2)
        middle_above = pl_above[middle_above_idx]
        farthest_above = pl_above[0]

        # sort platforms with coins
        # NOTE: if there aren't any, set it to the farthest platform
        if len(pl_coin) == 0:
            pl_coin = [farthest_above]
        # clear state and construct
        state = [P1.pos,            # 0, 1
                 nearest_below,     # 2, 3
                 nearest_above,     # 4, 5
                 middle_above,      # 6, 7
                 farthest_above,    # 8, 9
                 pl_coin[-1],       # 10, 11
                 P1.vel.y]          # 12
        # flatten state list
        return list(flatten(state))

    # get action using epsilon-greedy method to be taken from current
    # state
    def get_action(self, state):
        # exploration
        if random.uniform(0, 1) > self.epsilon:
            return random.randrange(0, self.action_size)
        # exploitation; get action from pred_model and take the biggest
        # q value (best action)
        else:
            state = np.array(state)
            # reshape state array to feed into NN
            state = state.reshape(1, self.state_size)
            return np.argmax(self.model.pred_model.predict(state))

    # step function takes in action, moves agent to next state and returns
    # [next_state, reward, done]
    def play_step(self, P1, action):
        done = False

        P1.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # inject actions into game
        if action < 3:
            P1.short_jump()
        elif action < 6:
            P1.long_jump()

        # end of episode here
        if P1.rect.top > Game.HEIGHT:
            done = True

        # exit this if done is True
        if done is not True:
            # scroll screen up if player goes above set height
            if P1.rect.top <= Game.HEIGHT / 3:
                # move player with velocity
                P1.pos.y += abs(P1.vel.y)
                # move platforms and coins as well with velocity
                for plat in Game.platforms:
                    plat.rect.y += abs(P1.vel.y)
                    if plat.rect.top >= Game.HEIGHT:
                        plat.kill()

                for coin in Game.coins:
                    coin.rect.y += abs(P1.vel.y)
                    if coin.rect.top >= Game.HEIGHT:
                        coin.kill()

            Game.plat_gen()
            Game.displaysurface.blit(Game.background, (0, 0))

            f = pygame.font.SysFont("Verdana", 20)
            g = f.render(str(P1.score), True, (123, 255, 0))
            Game.displaysurface.blit(g, (Game.WIDTH / 2, 10))

            for entity in Game.all_sprites:
                Game.displaysurface.blit(entity.surf, entity.rect)
                # inject left/right actions
                entity.move(P1, action)

            for coin in Game.coins:
                Game.displaysurface.blit(coin.image, coin.rect)
                coin.update(P1)

            # get cumulative reward from game
            reward = P1.score

        else:
            # set negative reward if done is true [game over]
            reward = P1.score + self.game_over_reward

        # observed state after executing the action
        # NOTE: even if done is set, we still get next_state which would
        # be the same as the last obtained state
        next_state = self.get_state(P1)
        # debug info
        show_state(next_state)
        # update display
        pygame.display.update()
        FramePerSec.tick(Game.FPS)
        return next_state, reward, done

# utils
# flatten list
def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten(item):
                yield x
        else:
            yield item

# display state
def show_state(state):
    # display state vector
    debugfont = pygame.font.SysFont("Verdana", 14)
    # player pos
    player_pos = [state[0], state[1]]
    debugsurface = debugfont.render(str(player_pos), True, (0, 0, 0))
    Game.displaysurface.blit(debugsurface, player_pos)

    # nearest platforms - below - near | above - near, middle, far
    for i in range(2, 9, 2):
        if i == 2:
            # color for platform below
            cl = (255, 0, 0)
        else:
            # color for platforms above
            cl = (0, 0, 255)
        debugsurface = debugfont.render(str([state[i], state[i+1]]), True, cl)
        Game.displaysurface.blit(debugsurface, (state[i], state[i+1]))
        # draw connecting lines
        pygame.draw.line(Game.displaysurface, cl, player_pos, (state[i], state[i+1]))

    # nearest coin platform
    debugsurface = debugfont.render(str([state[10], state[11]]), True, (0, 255, 0))
    Game.displaysurface.blit(debugsurface, (state[10], state[11]))
