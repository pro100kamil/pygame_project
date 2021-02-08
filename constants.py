import pygame

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750
FPS = 30
GRAVITY = 10 / FPS

screen = pygame.display.set_mode(SIZE)
# группы спрайтов
all_sprites = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
