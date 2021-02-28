import pygame
from sound_manager import SoundManager
from collections import namedtuple

TILE_SIDE = 50  # размер одной клетки
SIZE = WIDTH, HEIGHT = 1000, 700  # размер игрового окна
FPS = 30
GRAVITY = 12 / FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT + TILE_SIDE))
pygame.display.set_icon(pygame.image.load('data/for menu/Ninja Frog.png'))
game_screen = pygame.Surface(SIZE)

MAIN_HERO = None
NOW_LEVEL = None
KOL_LEVELS = 8  # количество уровней

clock = pygame.time.Clock()
# группы спрайтов
all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
checkpoints = pygame.sprite.Group()
player_group = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
backpacks_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
potions_group = pygame.sprite.Group()
chameleons = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()

sound_manager = SoundManager()  # звуковой класс

# Параметры героев
HERO_PARAMETERS = namedtuple('hero_parameters', 'damage speed health')
# name: (damage, speed, health)
HEROES = {'Ninja Frog': HERO_PARAMETERS(15, 7, 100),
          'Pink Man': HERO_PARAMETERS(20, 4, 120),
          'Virtual Guy': HERO_PARAMETERS(15, 6, 95),
          'Mask Dude': HERO_PARAMETERS(15, 5, 100)}
