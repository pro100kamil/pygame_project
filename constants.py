import pygame

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750  # size game_screen
FPS = 30
GRAVITY = 10 / FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT + TILE_SIDE))
game_screen = pygame.Surface(SIZE)
# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
