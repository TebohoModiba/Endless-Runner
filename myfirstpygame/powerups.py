import pygame
import random
import math
from settings import *


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COIN_COL,  (10, 10), 10)
        pygame.draw.circle(self.image, (200,160,0),(10, 10), 10, 2)
        pygame.draw.circle(self.image, (255,240,100),(7, 7), 4)
        self.rect       = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed      = 0
        self.base_y     = y
        self.tick       = random.randint(0, 60)

    def update(self):
        self.tick       += 1
        self.rect.y      = int(self.base_y + math.sin(self.tick * 0.1) * 5)
        self.rect.x     -= 7
        if self.rect.right < 0:
            self.kill()


class CoinRow:
    """Spawns a row of coins for the magnet and collection."""
    @staticmethod
    def spawn(group, all_sprites, count=5):
        x = WIDTH + 50
        y = GROUND_Y - random.randint(60, 120)
        for i in range(count):
            c = Coin(x + i * 30, y)
            group.add(c)
            all_sprites.add(c)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, speed):
        super().__init__()
        self.kind  = kind
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw()
        self.rect            = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 300),
                                GROUND_Y - random.randint(20, 80))
        self.speed = speed
        self.tick  = 0

    def _draw(self):
        cx, cy = 16, 16
        if self.kind == "shield":
            pygame.draw.circle(self.image, SHIELD_COL, (cx, cy), 14)
            pygame.draw.circle(self.image, WHITE,      (cx, cy), 14, 2)
            pygame.draw.polygon(self.image, WHITE,
                                [(cx, cy-8),(cx-6,cy+4),(cx+6,cy+4)])
        elif self.kind == "magnet":
            pygame.draw.rect(self.image, MAGNET_COL, (4, 4, 24, 14), border_radius=4)
            pygame.draw.rect(self.image, (180,0,180),(4, 18, 8,  10))
            pygame.draw.rect(self.image, (180,0,180),(20,18, 8,  10))
            pygame.draw.circle(self.image, WHITE, (8,  18), 4)
            pygame.draw.circle(self.image, WHITE, (24, 18), 4)
        elif self.kind == "multiplier":
            pygame.draw.circle(self.image, MULTI_COL, (cx, cy), 14)
            font = pygame.font.SysFont("Arial", 14, bold=True)
            txt  = font.render("x2", True, BLACK)
            self.image.blit(txt, txt.get_rect(center=(cx, cy)))

    def update(self):
        self.tick   += 1
        self.rect.x -= self.speed
        self.rect.y  = self.rect.y + int(math.sin(self.tick * 0.08) * 1)
        if self.rect.right < 0:
            self.kill()


def spawn_powerup(group, all_sprites, speed):
    kind = random.choice(["shield", "magnet", "multiplier"])
    p    = PowerUp(kind, speed)
    group.add(p)
    all_sprites.add(p)