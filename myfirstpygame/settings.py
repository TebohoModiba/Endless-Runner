WIDTH, HEIGHT  = 900, 500
FPS            = 60
GROUND_Y       = HEIGHT - 80

# Colors
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
SKY        = (135, 206, 235)
GROUND_COL = (80,  60,  40)
PLAYER_COL = (30,  100, 200)
OBS_COL    = (200, 50,  50)
FLY_COL    = (200, 130, 0)
SUN_COL    = (255, 220, 50)
CLOUD_COL  = (240, 240, 240)

# Power-up colors
SHIELD_COL  = (50,  180, 255)
MAGNET_COL  = (220, 50,  220)
MULTI_COL   = (255, 200, 0)
COIN_COL    = (255, 210, 0)

# Difficulty settings — (min_cooldown, max_cooldown, base_speed)
# (fly_min and fly_max are kept for compatibility but not used in unified spawn)
DIFFICULTIES = {
    "Easy":   (90,  150, 5.0),
    "Medium": (70,  130, 7.0),
    "Hard":   (50,  100, 10.0),
}