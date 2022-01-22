import pygame
from pygame.locals import *
import sys
import time
import Platformer_Final

FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((Platformer_Final.WIDTH, Platformer_Final.HEIGHT))

# get current state
def get_state():
    pass

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

    if P1.rect.top <= Platformer_Final.HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
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

    pygame.display.update()
    FramePerSec.tick(Platformer_Final.FPS)
