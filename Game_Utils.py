import pygame
from pygame.locals import *
import sys
import time
import Platformer_Final

FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((Platformer_Final.WIDTH, Platformer_Final.HEIGHT))

# sort platform list based on y coordinate
def sort_rule(e):
    return e[1]

# get current state
# [Player.x, Player.y, Platform1.x, Platform1.y,
#  Platform2.x, Platform2.y,
#  Platform3.x, Platform3.y,
#  Coin1.x, Coin1.y]
def get_state(P1):
    state = []
    coin_platform = []
    # filter platforms
    for p_entity in Platformer_Final.platforms:
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
    if len(coin_platform) == 0:
        coin_platform = [farthest]
    # clear state and construct
    state = [P1.pos, nearest, middle, farthest, coin_platform[-1]]

    return state

def show_state(state):
    # display state vector
    debugFont = pygame.font.SysFont("Verdana", 14)
    # player pos
    debugSurface = debugFont.render(str(state[0]), True, (0, 0, 0))
    displaysurface.blit(debugSurface, state[0])
    # nearest platform
    debugSurface = debugFont.render(str(state[1]), True, (0, 0, 255))
    displaysurface.blit(debugSurface, state[1])
    # middle platform
    debugSurface = debugFont.render(str(state[2]), True, (0, 0, 255))
    displaysurface.blit(debugSurface, state[2])
    # farthest platform
    debugSurface = debugFont.render(str(state[3]), True, (0, 0, 255))
    displaysurface.blit(debugSurface, state[3])
    # nearest coin platform
    debugSurface = debugFont.render(str(state[4]), True, (255, 0, 0))
    displaysurface.blit(debugSurface, state[4])

# step function takes in action, moves agent to next state
# and returns [next_state, reward, done]
def play_step(P1):
    P1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()

    # end of episode here
    if P1.rect.top > Platformer_Final.HEIGHT:
        for entity in Platformer_Final.all_sprites:
            entity.kill()
            time.sleep(1)
            displaysurface.fill((255, 0, 0))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()

    # scroll screen up if player goes above 1/2 of the screen height
    if P1.rect.top <= Platformer_Final.HEIGHT / 2:
        # move player with velocity
        P1.pos.y += abs(P1.vel.y)
        # move platforms and coins as well with velocity
        for plat in Platformer_Final.platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= Platformer_Final.HEIGHT:
                plat.kill()

        for coin in Platformer_Final.coins:
            coin.rect.y += abs(P1.vel.y)
            if coin.rect.top >= Platformer_Final.HEIGHT:
                coin.kill()

    Platformer_Final.plat_gen()
    displaysurface.blit(Platformer_Final.background, (0, 0))

    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (123, 255, 0))
    displaysurface.blit(g, (Platformer_Final.WIDTH / 2, 10))

    for entity in Platformer_Final.all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move(P1)

    for coin in Platformer_Final.coins:
        displaysurface.blit(coin.image, coin.rect)
        coin.update(P1)

    state = get_state(P1)
    show_state(state)

    pygame.display.update()
    FramePerSec.tick(Platformer_Final.FPS)
