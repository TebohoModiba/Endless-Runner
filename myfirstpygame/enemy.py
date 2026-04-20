import pygame
import random
import math
from settings import *


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        w = random.randint(20, 40)
        h = random.randint(40, 70)
        self.image = pygame.Surface((w, h + 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, OBS_COL, (0, 10, w, h), border_radius=4)
        for i in range(0, w, 10):
            pygame.draw.polygon(self.image, (160, 30, 30),
                                [(i, 10), (i + 5, 0), (min(i + 10, w), 10)])
        self.rect            = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 200), GROUND_Y)
        self.speed           = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class FlyingObstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((50, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, FLY_COL, (5, 5, 40, 14))
        pygame.draw.polygon(self.image, FLY_COL, [(0,  8), (15,  0), (15, 8)])
        pygame.draw.polygon(self.image, FLY_COL, [(35, 0), (50,  8), (35, 8)])
        pygame.draw.circle(self.image, BLACK, (44, 10), 3)
        self.rect            = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 200), GROUND_Y - 80)
        self.speed           = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class BouncingBall(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.radius = random.randint(16, 26)
        size        = self.radius * 2
        self.image  = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 60, 200), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, (220, 120, 240), (self.radius - 5, self.radius - 5), self.radius // 3)
        self.rect       = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 200), GROUND_Y)
        self.speed      = speed
        self.vel_y      = -16
        self.bounce_count = 0

    def update(self):
        self.rect.x -= self.speed
        self.vel_y  += 1
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y       = -14 + self.bounce_count
            self.bounce_count = min(self.bounce_count + 1, 8)
        if self.rect.right < 0:
            self.kill()


class SpinningBlade(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.size   = 40
        self.angle  = 0
        self.speed  = speed
        self._base  = self._draw_blade()
        self.image  = self._base.copy()
        self.rect   = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 200), GROUND_Y)

    def _draw_blade(self):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        cx, cy = self.size // 2, self.size // 2
        for i in range(4):
            angle = math.radians(i * 90)
            x1 = cx + int(math.cos(angle) * 18)
            y1 = cy + int(math.sin(angle) * 18)
            x2 = cx + int(math.cos(angle + 0.5) * 8)
            y2 = cy + int(math.sin(angle + 0.5) * 8)
            x3 = cx + int(math.cos(angle - 0.5) * 8)
            y3 = cy + int(math.sin(angle - 0.5) * 8)
            pygame.draw.polygon(surf, (200, 50, 50), [(x1, y1), (x2, y2), (x3, y3)])
        pygame.draw.circle(surf, (150, 30, 30), (cx, cy), 6)
        return surf

    def update(self):
        self.rect.x -= self.speed
        self.angle   = (self.angle + 8) % 360
        self.image   = pygame.transform.rotate(self._base, self.angle)
        old_bottom   = self.rect.bottom
        old_left     = self.rect.left
        self.rect    = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.left   = old_left
        if self.rect.right < 0:
            self.kill()


class FallingRock(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        size       = random.randint(24, 40)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        points     = []
        for i in range(7):
            angle = math.radians(i * (360 / 7))
            r     = size // 2 - random.randint(2, 6)
            cx, cy = size // 2, size // 2
            points.append((cx + int(math.cos(angle) * r),
                           cy + int(math.sin(angle) * r)))
        pygame.draw.polygon(self.image, (130, 110, 90), points)
        pygame.draw.polygon(self.image, (100, 80,  60), points, 2)
        self.rect       = self.image.get_rect()
        self.rect.x     = random.randint(200, WIDTH - 50)
        self.rect.y     = -50
        self.speed      = speed
        self.vel_y      = random.randint(4, 8)
        self.rot_angle  = 0
        self._base      = self.image.copy()

    def update(self):
        self.rect.x    -= self.speed * 0.3
        self.rect.y    += self.vel_y
        self.rot_angle  = (self.rot_angle + 4) % 360
        self.image      = pygame.transform.rotate(self._base, self.rot_angle)
        old_center      = self.rect.center
        self.rect       = self.image.get_rect()
        self.rect.center = old_center
        if self.rect.top > HEIGHT:
            self.kill()


class MovingSpike(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((20, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, OBS_COL,    [(10, 0), (0, 50), (20, 50)])
        pygame.draw.polygon(self.image, (160,30,30),[(10, 0), (0, 50), (20, 50)], 2)
        self.rect            = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(0, 200), GROUND_Y)
        self.speed           = speed
        self.start_x         = self.rect.x
        self.amplitude       = random.randint(40, 80)
        self.freq            = random.uniform(0.03, 0.06)
        self.tick            = 0

    def update(self):
        self.tick   += 1
        self.rect.x -= self.speed
        self.rect.bottom = int(GROUND_Y + math.sin(self.tick * self.freq) * self.amplitude * 0.3)
        if self.rect.right < 0:
            self.kill()