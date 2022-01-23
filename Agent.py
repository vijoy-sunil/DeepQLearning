import Game
import pygame
from pygame.locals import *
import sys

FramePerSec = pygame.time.Clock()

# sort platform list based on y coordinate
def sort_rule(e):
    return e[1]

class Agent:
    def __init__(self):
        # parameters
        self.epsilon = 0.2
        self.gamma = 0.8

        # deep network
        self.model = None
        self.trainer = None

    # get current state
    # [Player.x, Player.y, Platform1.x, Platform1.y,
    #  Platform2.x, Platform2.y,
    #  Platform3.x, Platform3.y,
    #  Coin1.x, Coin1.y]
    def get_state(self, P1):
        state = []
        coin_platform = []
        # filter platforms
        for p_entity in Game.platforms:
            p_y = p_entity.rect.centery
            # Check if platform is visible and is above the player
            if p_y < 0 or p_y > P1.pos[1]:
                continue
            # save platforms with coin
            if p_entity.isCoin:
                coin_platform.append(p_entity.rect.center)
            state.append(p_entity.rect.center)

        # sort platforms
        state.sort(key=sort_rule)

        # limit number of platforms to 3, the NN will only see
        # 3 platforms in front - nearest and farthest and one in between
        nearest = state[-1]
        middle_idx = int(len(state) / 2)
        middle = state[middle_idx]
        farthest = state[0]

        # sort platforms with coins
        # NOTE: if there aren't any, set it to the farthest platform
        if len(coin_platform) == 0:
            coin_platform = [farthest]
        # clear state and construct
        state = [P1.pos, nearest, middle, farthest, coin_platform[-1]]
        return state

    def show_state(self, state):
        # display state vector
        debugfont = pygame.font.SysFont("Verdana", 14)
        # player pos
        debugsurface = debugfont.render(str(state[0]), True, (0, 0, 0))
        Game.displaysurface.blit(debugsurface, state[0])
        # nearest platform
        debugsurface = debugfont.render(str(state[1]), True, (0, 0, 255))
        Game.displaysurface.blit(debugsurface, state[1])
        # middle platform
        debugsurface = debugfont.render(str(state[2]), True, (0, 0, 255))
        Game.displaysurface.blit(debugsurface, state[2])
        # farthest platform
        debugsurface = debugfont.render(str(state[3]), True, (0, 0, 255))
        Game.displaysurface.blit(debugsurface, state[3])
        # nearest coin platform
        debugsurface = debugfont.render(str(state[4]), True, (255, 0, 0))
        Game.displaysurface.blit(debugsurface, state[4])

    # step function takes in action, moves agent to next state
    # and returns [next_state, reward, done]
    def play_step(self, P1, actions):
        next_state = []
        done = False

        P1.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # inject actions into game
        if actions[0] == 1 or actions[1] == 1 or actions[2] == 1:
            P1.short_jump()
        if actions[3] == 1 or actions[4] == 1 or actions[5] == 1:
            P1.long_jump()

        # end of episode here
        if P1.rect.top > Game.HEIGHT:
            done = True

        # exit this if done is True
        if done is not True:
            # scroll screen up if player goes above 1/2 of the screen height
            if P1.rect.top <= Game.HEIGHT / 2:
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
                entity.move(P1, actions)

            for coin in Game.coins:
                Game.displaysurface.blit(coin.image, coin.rect)
                coin.update(P1)

            # observed state after executing the action
            next_state = self.get_state(P1)
            # debug info
            self.show_state(next_state)

            pygame.display.update()
            FramePerSec.tick(Game.FPS)

        return next_state, P1.score, done
