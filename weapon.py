import os
import pygame
import pyganim

from constants import *
from functions import *

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750
FPS = 30
GRAVITY = 10 / FPS

pygame.init()
screen = pygame.display.set_mode(SIZE)


class Shuriken(pygame.sprite.Sprite):
    width, height = 25, 25

    move_anim = pyganim.PygAnimation(
        cut_sheet('move_shuriken.png', 1, 13, anim_delay=100))
    move_anim.play()

    def __init__(self, x, y, direction, range_flight=200):
        super().__init__(all_sprites)

        self.rect = pygame.Rect(x, y, Shuriken.width, Shuriken.height)
        self.image = pygame.Surface((Shuriken.width, Shuriken.height))

        self.image.fill('black')
        self.image.set_colorkey('black')

        self.direction = direction
        if self.direction == "right":
            Shuriken.move_anim.flip(True, False)
        self.range_flight = range_flight  # дальность полёта
        self.delta = self.range_flight / 26
        self.flown = 0  # сколько сюрикен уже пролетел
        # урон, который получит персонаж, если в него попадёт сюрикен
        self.damage = 10

    def move(self):
        if self.direction == "right":
            self.rect.x += self.delta
        else:
            self.rect.x -= self.delta
        self.flown += self.delta
        Shuriken.move_anim.blit(self.image, (0, 0))

    def update(self):
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy.get_hit(self.damage)
            self.kill()
        if self.flown + self.delta <= self.range_flight and \
                not pygame.sprite.spritecollideany(self, platforms) and \
                not pygame.sprite.spritecollideany(self, spikes_group):
            self.move()
        else:  # полёт закончен
            self.flown = 0
            self.kill()
