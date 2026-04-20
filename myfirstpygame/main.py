import pygame
import sys
import random
from settings   import *
from players    import Player
from enemy      import (Obstacle, FlyingObstacle, BouncingBall,
                        SpinningBlade, FallingRock, MovingSpike)
from background import Background, blend_theme
from powerups   import PowerUp, Coin, CoinRow, spawn_powerup
from sounds     import load_sounds

pygame.init()
screen     = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner")
clock      = pygame.time.Clock()
font       = pygame.font.SysFont("Arial", 28, bold=True)
small_font = pygame.font.SysFont("Arial", 20)
tiny_font  = pygame.font.SysFont("Arial", 16)

sounds = load_sounds()


# ── Difficulty select screen ──────────────────────────────────────────────────
def difficulty_screen():
    selected  = 1          # 0=Easy 1=Medium 2=Hard
    options   = ["Easy", "Medium", "Hard"]
    colors    = [(50,200,80), (255,180,0), (220,50,50)]
    bg        = Background()
    theme     = blend_theme(0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected - 1) % 3
                if event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % 3
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return options[selected]
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        bg.draw(screen, theme, 0)

        title = font.render("SELECT DIFFICULTY", True, BLACK)
        tip   = small_font.render("LEFT / RIGHT to choose   SPACE to confirm", True, (60,60,60))
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))
        screen.blit(tip,   tip.get_rect(center=(WIDTH//2,   HEIGHT//2 + 80)))

        for i, (name, col) in enumerate(zip(options, colors)):
            x      = WIDTH//2 + (i-1) * 200
            y      = HEIGHT//2
            box_w  = 150
            box_h  = 60
            box    = pygame.Rect(x - box_w//2, y - box_h//2, box_w, box_h)
            border = 4 if i == selected else 1
            pygame.draw.rect(screen, col,   box, border_radius=10)
            pygame.draw.rect(screen, WHITE, box, border, border_radius=10)
            lbl = font.render(name, True, WHITE if i != selected else BLACK)
            screen.blit(lbl, lbl.get_rect(center=(x, y)))

        pygame.display.flip()
        clock.tick(FPS)


# ── HUD with multiplier, shield, power-up timers ─────────────────────────────
def draw_full_hud(screen, score, high_score, speed, multiplier,
                  shield, magnet_timer, multi_timer, coins):

    # Score + best + speed
    screen.blit(font.render(f"Score: {int(score)}", True, BLACK), (20, 16))
    screen.blit(small_font.render(f"Best: {int(high_score)}", True,(80,80,80)), (20,48))
    screen.blit(small_font.render(f"Speed: {speed:.1f}", True,(80,80,80)), (WIDTH-140,16))
    screen.blit(small_font.render(f"Coins: {coins}", True, COIN_COL),       (WIDTH-140,40))

    # Multiplier badge
    mx = multiplier + (1 if multi_timer > 0 else 0)
    if mx > 1:
        badge = font.render(f"x{mx}", True, MULTI_COL)
        screen.blit(badge, (WIDTH//2 - badge.get_width()//2, 12))

    # Active power-up timers
    y = 80
    if shield:
        s = small_font.render("SHIELD ACTIVE", True, SHIELD_COL)
        screen.blit(s, (20, y)); y += 24
    if magnet_timer > 0:
        bar_w = int((magnet_timer / (FPS * 8)) * 120)
        pygame.draw.rect(screen, (80,80,80),  (20, y, 120, 12), border_radius=4)
        pygame.draw.rect(screen, MAGNET_COL,  (20, y, bar_w, 12), border_radius=4)
        screen.blit(tiny_font.render("MAGNET", True, MAGNET_COL), (148, y - 1))
        y += 20
    if multi_timer > 0:
        bar_w = int((multi_timer / (FPS * 6)) * 120)
        pygame.draw.rect(screen, (80,80,80),  (20, y, 120, 12), border_radius=4)
        pygame.draw.rect(screen, MULTI_COL,   (20, y, bar_w, 12), border_radius=4)
        screen.blit(tiny_font.render("x2 BOOST", True, MULTI_COL), (148, y - 1))


# ── Main game loop ────────────────────────────────────────────────────────────
def run_game(high_score, difficulty):
    # Difficulty values: (min_cooldown, max_cooldown, base_speed)
    obs_min, obs_max, base_speed = DIFFICULTIES[difficulty]

    player      = Player(sounds)
    all_sprites = pygame.sprite.Group(player)
    obstacles   = pygame.sprite.Group()   # all harmful obstacles
    coins       = pygame.sprite.Group()
    powerups    = pygame.sprite.Group()
    bg          = Background()

    score           = 0
    speed           = base_speed
    obs_timer       = 0          # frames until next obstacle can spawn
    powerup_timer   = 0
    coin_timer      = 0
    last_score_blip = 0
    coin_count      = 0

    # Multiplier state
    multiplier      = 1
    multi_tick      = 0
    multi_boost     = 0

    # Power-up state
    shield_active   = False
    magnet_timer    = 0

    while True:
        clock.tick(FPS)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    player.jump()

        keys = pygame.key.get_pressed()
        player.duck(keys[pygame.K_DOWN] or keys[pygame.K_s])

        # ── Timers ──
        if obs_timer > 0: obs_timer -= 1
        if powerup_timer > 0: powerup_timer -= 1
        if coin_timer > 0: coin_timer -= 1
        if magnet_timer > 0: magnet_timer -= 1
        if multi_boost  > 0: multi_boost  -= 1
        multi_tick    += 1

        # ── Multiplier level-up every 10 seconds ──
        if multi_tick >= FPS * 10:
            multi_tick  = 0
            multiplier  = min(multiplier + 1, 8)

        # ── Unified obstacle spawning (no clusters) ──
        if obs_timer == 0:
            # Choose obstacle type with weighted probabilities
            r = random.random()
            if r < 0.6:   # 60% ground obstacles
                kind = random.choice([Obstacle, BouncingBall, MovingSpike])
                o = kind(speed)
            elif r < 0.85: # 25% flying
                kind = random.choice([FlyingObstacle, SpinningBlade])
                o = kind(speed)
            else:          # 15% falling rock
                o = FallingRock(speed)

            # Avoid spawning if another obstacle is too close (within 200 pixels)
            too_close = any(abs(o.rect.x - obs.rect.x) < 200 for obs in obstacles)
            if not too_close:
                obstacles.add(o)
                all_sprites.add(o)
                # Set cooldown based on difficulty
                cooldown = random.randint(obs_min, obs_max)
                obs_timer = cooldown
            else:
                # Try again in 10 frames
                obs_timer = 10

        # ── Spawn power-ups ──
        if powerup_timer == 0 and random.randint(0, 500) < 5:
            spawn_powerup(powerups, all_sprites, speed)
            powerup_timer = random.randint(300, 500)

        # ── Spawn coins ──
        if coin_timer == 0 and random.randint(0, 140) < 5:
            CoinRow.spawn(coins, all_sprites, count=random.randint(3,7))
            coin_timer = random.randint(80, 140)

        # ── Magnet pulls coins ──
        if magnet_timer > 0:
            for coin in coins:
                dx = player.rect.centerx - coin.rect.centerx
                dy = player.rect.centery - coin.rect.centery
                dist = max(1, (dx**2 + dy**2)**0.5)
                coin.rect.x += int(dx / dist * 8)
                coin.rect.y += int(dy / dist * 8)

        # ── Update ──
        all_sprites.update()
        score += 0.1 * multiplier * (2 if multi_boost > 0 else 1)
        speed  = base_speed + score * 0.008

        theme  = blend_theme(score)
        bg.update(theme)

        # ── Score milestone sound ──
        if int(score) // 50 > last_score_blip:
            sounds["score"].play()
            last_score_blip = int(score) // 50

        # ── Coin collection ──
        hit_coins = pygame.sprite.spritecollide(player, coins, True)
        coin_count += len(hit_coins)

        # ── Power-up collection ──
        hit_pu = pygame.sprite.spritecollide(player, powerups, True)
        for pu in hit_pu:
            if pu.kind == "shield":
                shield_active = True
            elif pu.kind == "magnet":
                magnet_timer  = FPS * 8     # 8 seconds
            elif pu.kind == "multiplier":
                multi_boost   = FPS * 6     # 6 seconds

        # ── Collision with obstacles ──
        hit = pygame.sprite.spritecollide(player, obstacles, False,
                                          pygame.sprite.collide_mask)
        if hit:
            if shield_active:
                shield_active = False
                multiplier    = max(1, multiplier - 1)
                for h in hit:
                    h.kill()
            else:
                sounds["death"].play()
                pygame.time.wait(600)
                high_score = max(high_score, score)
                return score, high_score, coin_count

        # ── Draw ──
        bg.draw(screen, theme, score)
        obstacles.draw(screen)
        coins.draw(screen)
        powerups.draw(screen)
        screen.blit(player.image, player.rect)
        draw_full_hud(screen, score, high_score, speed, multiplier,
                      shield_active, magnet_timer, multi_boost, coin_count)
        pygame.display.flip()


# ── Start screen ──────────────────────────────────────────────────────────────
def start_screen():
    theme = blend_theme(0)
    bg    = Background()
    bg.draw(screen, theme, 0)
    t1 = font.render("ENDLESS RUNNER",      True, BLACK)
    t2 = small_font.render(
        "SPACE / UP = Jump  |  DOWN = Duck  |  Double jump supported",
        True, (60,60,60))
    t3 = small_font.render("Press SPACE to start", True, PLAYER_COL)
    screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
    screen.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2)))
    screen.blit(t3, t3.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
    pygame.display.flip()


def wait_for_space():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:   return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


# ── Game over screen ──────────────────────────────────────────────────────────
def game_over(score, high_score, coins, difficulty):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,150))
    screen.blit(overlay, (0,0))
    lines = [
        font.render("GAME OVER",              True, (220,50,50)),
        font.render(f"Score: {int(score)}",   True, WHITE),
        font.render(f"Best:  {int(high_score)}", True, MULTI_COL),
        small_font.render(f"Coins collected: {coins}   Difficulty: {difficulty}",
                          True, COIN_COL),
        small_font.render("SPACE to play again  |  ESC to quit", True, WHITE),
    ]
    y = HEIGHT//2 - 90
    for surf in lines:
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, y)))
        y += 50
    pygame.display.flip()


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    high_score = 0
    while True:
        start_screen()
        wait_for_space()
        difficulty = difficulty_screen()
        score, high_score, coins = run_game(high_score, difficulty)
        game_over(score, high_score, coins, difficulty)
        wait_for_space()


if __name__ == "__main__":
    main()