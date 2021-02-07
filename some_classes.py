import os
from random import choice

import pygame
import pyganim

from constants import *
from functions import *


class Platform(pygame.sprite.Sprite):
    """Платформы"""

    def __init__(self, x, y):
        super().__init__(platforms, all_sprites)

        self.image = pygame.transform.scale(load_image('grass.png'),
                                            (TILE_SIDE, TILE_SIDE))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Spikes(pygame.sprite.Sprite):
    """Шипы"""

    def __init__(self, x, y):
        super().__init__(spikes_group, all_sprites)

        self.image = pygame.transform.scale(load_image('spikes.png'),
                                            (TILE_SIDE, TILE_SIDE))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)
        # урон, который получит персонаж, если ударится о шипы
        self.damage = 30

    def get_damage(self):
        return self.damage


class Fruit(pygame.sprite.Sprite):
    """Фрукты (прибавляют игроку жизни)"""

    width, height = 32, 32

    fruits = ['Apple', 'Bananas', 'Cherries', 'Melon',
              'Kiwi', 'Pineapple', 'Strawberry', 'Orange']

    def __init__(self, x, y):
        super().__init__(fruits_group, all_sprites)

        self.rect = pygame.Rect(x, y, Fruit.width, Fruit.height)
        self.image = pygame.Surface((Fruit.width, Fruit.height))
        self.collected = False

        # каждый раз случайный фрукт
        self.anim_normal = pyganim.PygAnimation(cut_sheet(
            f'Fruits/{choice(Fruit.fruits)}.png', 1, 17, anim_delay=100))
        self.anim_normal.play()

        self.anim_collected = pyganim.PygAnimation(cut_sheet(
            f'Fruits/Collected.png', 1, 6, anim_delay=100))

        # кол-во жизней, которое получит герой, если возьмёт фрукт
        self.health = 10

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

        if not self.collected:  # Если не собран, обычная анимация
            self.anim_normal.blit(self.image, (0, 0))
        elif self.anim_collected.currentFrameNum == \
                self.anim_collected.numFrames - 1:
            # Если собран и анимация подходит к концу, спрайт удаляется
            self.anim_collected.stop()
            self.kill()
        else:
            self.anim_collected.blit(self.image, (0, 0))

    def collect(self):
        """Фрукт собран"""

        self.collected = True
        self.anim_collected.play()

    def is_collected(self):
        return self.collected

    def get_health(self):
        return self.health


class Camera:
    def __init__(self, width, height):
        self.view = pygame.Rect(0, 0, width, height)

    def apply(self, obj):
        """Сдвинуть объект obj на смещение камеры"""
        return obj.rect.move(self.view.topleft)

    def update(self, target):
        """Позиционировать камеру на объекте target"""
        self.view = self.set_camera(target)

    def set_camera(self, target):
        left, top, _, _ = target.rect
        _, _, width, height = self.view

        left, top = WIDTH / 2 - left, HEIGHT / 2 - top

        left = max(WIDTH - width, min(0, left))
        top = min(0, max(HEIGHT - height, top))

        return pygame.Rect(left, top, width, height)
