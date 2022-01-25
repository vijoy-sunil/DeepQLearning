import pygame
import random
import sys

pygame.init()
# 2 for two dimensional
vec = pygame.math.Vector2

HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DQN Game")
background = pygame.image.load("./Game_Files/sky.png")

# sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./Game_Files/mario.png")
        self.surf = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.surf.get_rect()

        # player spawn at random location on base platform
        self.pos = vec(random.randint(10, WIDTH - 30), 425)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0

        # rewards
        self.platform_land_reward = 1

    def move(self, P1, action):
        self.acc = vec(0, 0.5)

        # inject actions into game
        if action == 1 or action == 4 or action == 6:
            self.acc.x = -ACC
        if action == 2 or action == 5 or action == 7:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # screen wrapping
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        # update rect with new position (after movement)
        self.rect.midbottom = self.pos

    def long_jump(self):
        # jump only if player is in contact with a platform
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def short_jump(self):
        # jump only if player is in contact with a platform
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -10

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            # when player lands on a platform
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0].point == True:
                        # This prevents the player from gaining points from
                        # jumping onto the same platform over and over to
                        # gain points
                        hits[0].point = False
                        self.score += self.platform_land_reward
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.image = pygame.image.load("./Game_Files/coin.png")
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # rewards
        self.coin_reward = 5

    def update(self, P1):
        if self.rect.colliderect(P1.rect):
            P1.score += self.coin_reward
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, width=0, height=18):
        super().__init__()

        if width == 0:
            width = random.randint(50, 120)

        self.image = pygame.image.load("./Game_Files/platform.png")
        self.surf = pygame.transform.scale(self.image, (width, height))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 70)))

        # the “point” attribute for the Platform which determines
        # whether the platform will give the player a point if he
        # lands on it or not.
        self.point = True
        self.moving = True
        # Disable moving platforms
        # self.speed = random.randint(-1, 1)
        self.speed = 0

        if self.speed == 0:
            self.moving = False

        # presence of coin
        self.isCoin = False

    # moving platforms
    def move(self, P1, action):
        hits = self.rect.colliderect(P1.rect)
        if self.moving == True:
            self.rect.move_ip(self.speed, 0)

            # move player along with platform
            if hits:
                P1.pos += (self.speed, 0)

            # platform screen wrapping
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

    def generate_coin(self):
        if self.speed == 0:
            # when moving platform is disabled, we need to
            # randomly generate coins
            coins_prob = random.uniform(0.0, 1.0)
            if coins_prob > 0.85:
                self.isCoin = True
                coins.add(Coin((self.rect.centerx, self.rect.centery - 30)))

# check if platforms generated are too close
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (
                    abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        return False

# random level generation, When the player moves up, the
# screen shifts and these platforms become visible
def plat_gen():
    while len(platforms) < 7:
        width = random.randrange(50, 100)
        P = None
        C = True

        while C:
            P = Platform()
            # generate platforms off-screen so when the player moves
            # up it becomes visible
            P.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-50, 0))
            C = check(P, platforms)

        P.generate_coin()
        platforms.add(P)
        all_sprites.add(P)

def init_game():
    # base platform
    PT1 = Platform(450, 40)
    PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))
    PT1.moving = False
    PT1.point = False

    P1 = Player()

    all_sprites.add(PT1)
    all_sprites.add(P1)
    platforms.add(PT1)

    # generate platforms for initial screen, will only run
    # once at the start
    for x in range(random.randint(5, 6)):
        C = True
        Pl = Platform()
        while C:
            Pl = Platform()
            C = check(Pl, platforms)
        Pl.generate_coin()
        platforms.add(Pl)
        all_sprites.add(Pl)

    return P1

def reset_game():
    # kill all sprites
    for entity in all_sprites:
        entity.kill()
    for entity in platforms:
        entity.kill()
    for entity in coins:
        entity.kill()
    displaysurface.fill((255, 0, 0))
    pygame.display.update()

def safe_close():
    # safe close the game
    reset_game()
    pygame.quit()
    sys.exit()
