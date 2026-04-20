import pygame
from settings import *


def draw_hud(screen, font, small_font, score, high_score, speed):
    score_surf = font.render(f"Score: {int(score)}", True, BLACK)
    hi_surf    = small_font.render(f"Best: {int(high_score)}", True, (80, 80, 80))
    spd_surf   = small_font.render(f"Speed: {speed:.1f}", True, (80, 80, 80))
    screen.blit(score_surf, (20, 16))
    screen.blit(hi_surf,    (20, 48))
    screen.blit(spd_surf,   (WIDTH - 140, 16))


def game_over_screen(screen, font, small_font, score, high_score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))
    title = font.render("GAME OVER",                 True, (220, 50,  50))
    sc    = font.render(f"Score: {int(score)}",      True, (255, 255, 255))
    hi    = font.render(f"Best:  {int(high_score)}", True, (255, 220, 50))
    tip   = small_font.render("SPACE to play again  |  ESC to quit", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
    screen.blit(sc,    sc.get_rect(center=(WIDTH // 2,    HEIGHT // 2 - 20)))
    screen.blit(hi,    hi.get_rect(center=(WIDTH // 2,    HEIGHT // 2 + 30)))
    screen.blit(tip,   tip.get_rect(center=(WIDTH // 2,   HEIGHT // 2 + 90)))
    pygame.display.flip()