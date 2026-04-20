import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, sounds):
        super().__init__()
        self.sounds      = sounds
        self.w, self.h   = 30, 60
        self.ducking     = False
        self.frame       = 0
        self.anim_timer  = 0
        self.frames      = self._build_frames()
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect()
        self.rect.bottomleft = (120, GROUND_Y)
        self.vel_y       = 0
        self.on_ground   = True
        self.jump_count  = 0

    def _draw_body(self, surf, leg1, leg2):
        """Draw body on a surface with given leg positions."""
        surf.fill((0, 0, 0, 0))
        # Leg 1
        pygame.draw.rect(surf, (20, 70, 160),
                         (5 + leg1[0], 40 + leg1[1], 8, 20))
        # Leg 2
        pygame.draw.rect(surf, (20, 70, 160),
                         (17 + leg2[0], 40 + leg2[1], 8, 20))
        # Body
        pygame.draw.rect(surf, PLAYER_COL, (3, 18, 24, 24), border_radius=4)
        # Head
        pygame.draw.circle(surf, PLAYER_COL, (15, 12), 12)
        # Eye
        pygame.draw.circle(surf, WHITE, (20, 10), 3)
        pygame.draw.circle(surf, BLACK, (21, 10), 1)
        # Arm swing
        pygame.draw.line(surf, PLAYER_COL, (3, 24), (0, 34), 3)
        pygame.draw.line(surf, PLAYER_COL, (27, 24), (30, 34), 3)

    def _build_frames(self):
        """Build 4 running frames with different leg positions."""
        # Each tuple is (x_offset, y_offset) for leg1 and leg2
        leg_positions = [
            ((-3, -4), ( 3,  4)),   # frame 0 — stride forward/back
            ((-1, -2), ( 1,  2)),   # frame 1 — mid stride
            (( 3,  4), (-3, -4)),   # frame 2 — opposite stride
            (( 1,  2), (-1, -2)),   # frame 3 — mid stride back
        ]
        frames = []
        for leg1, leg2 in leg_positions:
            surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            self._draw_body(surf, leg1, leg2)
            frames.append(surf)
        return frames

    def _duck_surface(self):
        surf = pygame.Surface((self.w, 30), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, PLAYER_COL, (0, 0, 30, 30), border_radius=4)
        pygame.draw.circle(surf, PLAYER_COL, (15, -8), 12)
        pygame.draw.circle(surf, WHITE, (20, -10), 3)
        pygame.draw.circle(surf, BLACK, (21, -10), 1)
        return surf

    def jump(self):
        if self.jump_count < 2:
            self.vel_y      = -18
            self.on_ground  = False
            if self.jump_count == 0:
                self.sounds["jump"].play()
            else:
                self.sounds["double_jump"].play()
            self.jump_count += 1

    def duck(self, ducking):
        if ducking == self.ducking:
            return
        bottom       = self.rect.bottom
        self.ducking = ducking
        self.h       = 30 if ducking else 60
        self.rect        = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.left   = 120

    def update(self):
        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y       = 0
            self.on_ground   = True
            self.jump_count  = 0

        # Animation
        if self.ducking:
            self.image = self._duck_surface()
        elif self.on_ground:
            self.anim_timer += 1
            if self.anim_timer >= 6:   # change frame every 6 ticks = ~10fps walk cycle
                self.anim_timer = 0
                self.frame      = (self.frame + 1) % 4
            self.image = self.frames[self.frame]
        else:
            # In air — freeze on frame 0 (legs together)
            self.image = self.frames[0]