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
        self.mask = pygame.mask.from_surface(self.image)


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


class Saw(pygame.sprite.Sprite):
    """Пила"""

    width, height = 38, 38

    def __init__(self, x, y):
        super().__init__(spikes_group, all_sprites)

        self.rect = pygame.Rect(x, y + TILE_SIDE // 2, Saw.width, Saw.height)
        self.image = pygame.Surface((Saw.width, Saw.height))

        self.anim_normal = pyganim.PygAnimation(cut_sheet(
            f'Saw/On (38x38).png', 1, 8, anim_delay=100))
        self.anim_normal.play()

        # урон, который получит персонаж, если ударится о шипы
        self.damage = 30

        self.speed = 5

        self.x_vel, self.y_vel = -self.speed, 0

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

        check_on_ground = pygame.sprite.spritecollideany(self, platforms)
        if check_on_ground is None:
            self.rect.x -= self.x_vel
            self.rect.y -= self.y_vel
            if self.x_vel:
                self.y_vel = -self.speed if self.x_vel > 0 else self.speed
                if self.y_vel < 0:
                    self.rect.x -= Saw.width // 3
                else:
                    self.rect.x += Saw.width // 3
                self.x_vel = 0
            else:
                self.x_vel = -self.speed if self.y_vel < 0 else self.speed
                if self.x_vel > 0:
                    self.rect.y -= Saw.width // 3
                else:
                    self.rect.y += Saw.width // 3
                self.y_vel = 0

        self.anim_normal.blit(self.image, (0, 0))

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


class Backpack(pygame.sprite.Sprite):
    """Рюкзак с сюрикенами"""

    width, height = 32, 32

    def __init__(self, x, y):
        super().__init__(fruits_group, all_sprites)

        self.rect = pygame.Rect(x, y, Fruit.width, Fruit.height)
        self.image = pygame.transform.scale(load_image('backpack.png', -1),
                                            (Backpack.width, Backpack.height))

        # кол-во сюрикенов, которое получит герой, если возьмёт рюкзак
        self.kol = 10

    def collect(self):
        """Фрукт собран"""
        self.kill()

    def is_collected(self):
        # если спрайт существует, то он не собран
        return False

    def get_kol(self):
        return self.kol


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


class Particles(pygame.sprite.Sprite):
    orig_pic = load_image('Dust Particle.png')
    orig_pic = pygame.transform.scale(orig_pic, (10, 10))
    orig_side = orig_pic.get_height()
    pictures = [orig_pic, pygame.transform.scale(orig_pic, [orig_side - 5] * 2)]

    def __init__(self, direction, position):
        super().__init__(all_sprites)

        self.start_frame = 0

        self.image = choice(Particles.pictures)
        self.rect = self.image.get_rect()

        self.x_vel = 0.5 if direction == 'left' else -0.5
        self.y_vel = choice([0, -1])

        if direction == 'left':
            self.rect.bottomleft = position
        elif direction == 'right':
            self.rect.bottomright = position

    def update(self):
        if self.start_frame == 2:
            self.kill()
            return

        self.rect = self.rect.move(self.x_vel, self.y_vel)
        self.start_frame += 1


class Checkpoint(pygame.sprite.Sprite):
    width, height = 64, 64

    def __init__(self, x, y, name):
        super().__init__(checkpoints, all_sprites)

        self.rect = pygame.Rect(x, y, Checkpoint.width, Checkpoint.height)
        self.image = pygame.Surface((Checkpoint.width, Checkpoint.height))

        self.moving = True

        if name == 'Start':
            self.stay_anim = pyganim.PygAnimation(cut_sheet(
                'Start/Idle.png', 1, 1, anim_delay=100))
            self.moving_anim = pyganim.PygAnimation(cut_sheet(
                'Start/Moving.png', 1, 17, anim_delay=100))
        elif name == 'End':
            self.stay_anim = pyganim.PygAnimation(cut_sheet(
                'End/Idle.png', 1, 10, anim_delay=100))
            self.moving_anim = pyganim.PygAnimation(cut_sheet(
                'End/Moving.png', 1, 26, anim_delay=100))

        self.stay_anim.play()
        self.moving_anim.play()

        self.name = name

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')
        if self.moving_anim.currentFrameNum + 1 == self.moving_anim.numFrames:
            self.moving = False
        if self.moving:
            self.moving_anim.blit(self.image, (0, 0))
        else:
            self.stay_anim.blit(self.image, (0, 0))

    def get_name(self):
        return self.name


class Potion(pygame.sprite.Sprite):
    """Зелье скорости или урона"""

    width, height = 27, 32

    def __init__(self, x, y):
        super().__init__(potions_group, all_sprites)

        self.name = choice(['speed', 'damage'])
        self.rect = pygame.Rect(x, y, Potion.width, Potion.height)
        self.image = pygame.Surface((Potion.width, Potion.height))
        self.collected = False

        if self.name == 'speed':
            self.anim_normal = pyganim.PygAnimation(cut_sheet(
                f'PotionsSheet.png', 8, 8, anim_delay=500)[8:12])
        else:
            self.anim_normal = pyganim.PygAnimation(cut_sheet(
                f'PotionsSheet.png', 8, 8, anim_delay=500)[0:4])
        self.anim_normal.scale2x()
        self.anim_normal.play()

        self.anim_collected = pyganim.PygAnimation(cut_sheet(
            f'Potions/Collected.png', 1, 6, anim_delay=100))

        # Добавление скорости/урона и длительность буста
        self.boost = 2 if self.name == 'speed' else 30
        self.duration = 5000 if self.name == 'speed' else 8000

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
        """Зелье собрано"""
        self.collected = True
        self.anim_collected.play()

    def is_collected(self):
        return self.collected

    def get_name(self):
        return self.name

    def get_boost(self):
        return self.boost

    def get_duration(self):
        return self.duration
