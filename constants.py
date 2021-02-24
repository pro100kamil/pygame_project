import pygame

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750  # размер игрового окна
FPS = fps = 30
GRAVITY = 12 / FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT + TILE_SIDE))
game_screen = pygame.Surface(SIZE)

clock = pygame.time.Clock()
# группы спрайтов
all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
checkpoints = pygame.sprite.Group()
player_group = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
potions_group = pygame.sprite.Group()
chameleons = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
