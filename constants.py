import pygame
import pygame_gui
from sound_manager import SoundManager

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 1000, 700  # размер игрового окна
FPS = 30
GRAVITY = 12 / FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT + TILE_SIDE))
pygame.display.set_icon(pygame.image.load('data/for menu/Ninja Frog.png'))
game_screen = pygame.Surface(SIZE)

MAIN_HERO = None
NOW_LEVEL = None

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

sound_manager = SoundManager()
