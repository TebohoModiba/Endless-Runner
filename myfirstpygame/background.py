import pygame
import random
from settings import *

# --- Color themes for each time of day ---
THEMES = {
    "day": {
        "sky_top":    (100, 180, 255),
        "sky_bottom": (180, 220, 255),
        "ground":     (80,  60,  40),
        "mountain1":  (100, 140, 100),
        "mountain2":  (130, 170, 130),
        "star":       None,
        "sun_moon":   (255, 220, 50),
        "cloud":      (240, 240, 240),
    },
    "sunset": {
        "sky_top":    (30,  30,  80),
        "sky_bottom": (255, 100, 30),
        "ground":     (60,  40,  30),
        "mountain1":  (80,  50,  60),
        "mountain2":  (110, 70,  80),
        "star":       None,
        "sun_moon":   (255, 160, 20),
        "cloud":      (255, 160, 100),
    },
    "night": {
        "sky_top":    (5,   5,   20),
        "sky_bottom": (20,  20,  60),
        "ground":     (30,  25,  35),
        "mountain1":  (20,  20,  40),
        "mountain2":  (30,  30,  55),
        "star":       (255, 255, 200),
        "sun_moon":   (220, 220, 180),
        "cloud":      (50,  50,  80),
    },
}

def get_theme(score):
    """Return current theme and next theme plus blend factor (0.0 to 1.0)."""
    if score < 400:
        return THEMES["day"], THEMES["day"], 0.0
    elif score < 500:
        return THEMES["day"], THEMES["sunset"], (score - 400) / 100
    elif score < 900:
        return THEMES["sunset"], THEMES["sunset"], 0.0
    elif score < 1000:
        return THEMES["sunset"], THEMES["night"], (score - 900) / 100
    else:
        return THEMES["night"], THEMES["night"], 0.0

def lerp_color(c1, c2, t):
    """Smoothly interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def blend_theme(score):
    """Return a single blended theme dict based on score."""
    t1, t2, factor = get_theme(score)
    if factor == 0.0:
        return t1
    blended = {}
    for key in t1:
        if t1[key] is None or t2[key] is None:
            blended[key] = t2[key] if factor > 0.5 else t1[key]
        else:
            blended[key] = lerp_color(t1[key], t2[key], factor)
    return blended


class Star:
    def __init__(self):
        self.x    = random.randint(0, WIDTH)
        self.y    = random.randint(0, GROUND_Y - 100)
        self.size = random.choice([1, 1, 1, 2])
        self.twinkle_timer = random.randint(0, 60)

    def draw(self, screen, color, alpha):
        if color is None or alpha < 0.1:
            return
        self.twinkle_timer += 1
        brightness = 0.6 + 0.4 * abs((self.twinkle_timer % 60) / 30 - 1)
        c = tuple(min(255, int(color[i] * brightness)) for i in range(3))
        pygame.draw.circle(screen, c, (self.x, self.y), self.size)


class Mountain:
    """A scrolling mountain silhouette layer."""
    def __init__(self, speed, color_key, height_range, y_base, count=8):
        self.speed     = speed
        self.color_key = color_key
        self.y_base    = y_base
        self.peaks     = []
        x = 0
        while x < WIDTH + 300:
            w = random.randint(80, 180)
            h = random.randint(*height_range)
            self.peaks.append([x, h, w])
            x += w - random.randint(10, 40)

    def update(self):
        for p in self.peaks:
            p[0] -= self.speed
        # Recycle peaks that scroll off the left
        while self.peaks and self.peaks[0][0] + self.peaks[0][2] < 0:
            self.peaks.pop(0)
        # Add new peaks on the right
        last_x = self.peaks[-1][0] + self.peaks[-1][2] - random.randint(10, 40)
        while last_x < WIDTH + 200:
            w = random.randint(80, 180)
            h = random.randint(40, 120)
            self.peaks.append([last_x, h, w])
            last_x += w - random.randint(10, 40)

    def draw(self, screen, theme):
        color = theme[self.color_key]
        points = [(0, self.y_base)]
        for x, h, w in self.peaks:
            mid = x + w // 2
            points.append((x, self.y_base))
            points.append((mid, self.y_base - h))
            points.append((x + w, self.y_base))
        points.append((WIDTH, self.y_base))
        points.append((WIDTH, HEIGHT))
        points.append((0, HEIGHT))
        if len(points) > 3:
            pygame.draw.polygon(screen, color, points)


class Background:
    def __init__(self):
        self.stars     = [Star() for _ in range(80)]
        self.mountain1 = Mountain(1.0, "mountain2", (40,  100), GROUND_Y)
        self.mountain2 = Mountain(2.0, "mountain1", (60,  130), GROUND_Y)
        self.clouds    = []
        self.cloud_timer = 0

    def _spawn_cloud(self, theme):
        color = theme["cloud"]
        x     = WIDTH + random.randint(0, 200)
        y     = random.randint(30, 160)
        speed = random.uniform(1.0, 2.5)
        self.clouds.append([x, y, speed, color])

    def update(self, theme):
        self.mountain1.update()
        self.mountain2.update()

        self.cloud_timer += 1
        if self.cloud_timer > 80:
            self._spawn_cloud(theme)
            self.cloud_timer = 0

        for c in self.clouds:
            c[0] -= c[2]
        self.clouds = [c for c in self.clouds if c[0] > -150]

    def draw(self, screen, theme, score):
        # Sky gradient (two rects for top/bottom blend)
        top_rect    = pygame.Rect(0, 0, WIDTH, GROUND_Y // 2)
        bottom_rect = pygame.Rect(0, GROUND_Y // 2, WIDTH, GROUND_Y // 2)
        pygame.draw.rect(screen, theme["sky_top"],    top_rect)
        pygame.draw.rect(screen, theme["sky_bottom"], bottom_rect)

        # Stars (fade in during sunset/night)
        star_alpha = 0.0
        if score >= 400:
            star_alpha = min(1.0, (score - 400) / 200)
        for star in self.stars:
            star.draw(screen, theme["star"], star_alpha)

        # Sun or moon
        sun_x = WIDTH - 90
        sun_y = 70
        pygame.draw.circle(screen, theme["sun_moon"], (sun_x, sun_y), 38)
        # Moon craters at night
        if score >= 900:
            fade = min(1.0, (score - 900) / 100)
            if fade > 0.5:
                dark = lerp_color(theme["sun_moon"], (30, 30, 60), 0.4)
                pygame.draw.circle(screen, dark, (sun_x - 10, sun_y + 8),  7)
                pygame.draw.circle(screen, dark, (sun_x + 12, sun_y - 10), 5)
                pygame.draw.circle(screen, dark, (sun_x + 5,  sun_y + 14), 4)

        # Clouds
        for cx, cy, spd, color in self.clouds:
            self._draw_cloud(screen, int(cx), int(cy), color)

        # Mountains (back then front)
        self.mountain2.draw(screen, theme)
        self.mountain1.draw(screen, theme)

        # Ground
        pygame.draw.rect(screen, theme["ground"],
                         (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        edge = lerp_color(theme["ground"], (0, 0, 0), 0.3)
        pygame.draw.line(screen, edge, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    def _draw_cloud(self, screen, x, y, color):
        pygame.draw.ellipse(screen, color, (x,      y + 15, 60, 25))
        pygame.draw.ellipse(screen, color, (x + 20, y +  5, 50, 30))
        pygame.draw.ellipse(screen, color, (x + 50, y + 10, 50, 25))