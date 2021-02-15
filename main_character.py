import os
from random import choice
from collections import namedtuple

import pygame
import pyganim

from constants import *
from functions import *
from enemy import *
from some_classes import *
from weapon import Shuriken

hero_parameters = namedtuple('hero_parameters', 'damage speed health')
MAIN_HERO = 'Pink Man'
# name: (damage, speed, health)
heroes = {'Ninja Frog': hero_parameters(15, 5, 100),
          'Pink Man': hero_parameters(20, 4, 120),
          'Virtual Guy': hero_parameters(15, 7, 95),
          'Mask Dude': hero_parameters(15, 6, 100)}

pygame.init()


def load_level(filename):
    """Загрузка уровня"""
    filename = os.path.join('data', filename)
    # если файл не существует, то выходим
    if not os.path.isfile(filename):
        raise SystemExit(f"Файл с картой '{filename}' не найден")

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    new_player, x, y = None, None, None
    for y, row in enumerate(level_map):
        for x, elem in enumerate(row):
            if elem == '-':
                Platform(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '.':
                Spikes(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '*':
                Fruit(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'b':
                BouncedEnemy(x * TILE_SIDE, y * TILE_SIDE, 10)
            elif elem == 'w':
                WalkingEnemy(x * TILE_SIDE, y * TILE_SIDE, 2, 100)
            elif elem == '@':
                new_player = MainHero(x * TILE_SIDE - 18,
                                      y * TILE_SIDE + 18, MAIN_HERO)

    return new_player, (x + 1) * TILE_SIDE, (y + 1) * TILE_SIDE


class BaseHero(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__(all_sprites)

        self.width, self.height = width, height

        self.start_x, self.start_y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height))
        self.x_vel, self.y_vel = None, None
        self.on_ground = False

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_position(self):
        return self.rect.x, self.rect.y


class MainHero(BaseHero):
    width, height = 32, 32

    def __init__(self, x, y, name):
        super().__init__(x, y, MainHero.width, MainHero.height)

        self.direction = "right"
        self.speed = heroes[name].speed
        self.jump, self.x_vel, self.y_vel = 0, 0, 0
        self.height_jump = 10  # показатель высоты прыжка
        self.double_jump = False  # происходит ли сейчас двойной прыжок
        self.got_hit = False  # Время последнего удара
        self.health = heroes[name].health  # количество жизней
        # урон, который наносит герой при напрыгивании на врага
        self.damage = heroes[name].damage

        self.number_shurikens = 10  # кол-во оставшихся сюрикенов

        self.mask = pygame.mask.from_surface(self.image)

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            f'{name}/Hit (32x32).png', 1, 7, anim_delay=100)),

            'jump': pyganim.PygAnimation(cut_sheet(
                f'{name}/Jump (32x32).png', 1, 1, anim_delay=100)),

            'double_jump': pyganim.PygAnimation(cut_sheet(
                f'{name}/Double Jump (32x32).png', 1, 6, anim_delay=100)),

            'fall': pyganim.PygAnimation(cut_sheet(
                f'{name}/Fall (32x32).png', 1, 1, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                f'{name}/Run (32x32).png', 1, 12, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                f'{name}/Idle (32x32).png', 1, 11, anim_delay=100))
        }
        for anim in self.animations.values():
            anim.play()

    def flip(self):
        """Разворот всех анимаций спрайтов"""
        for anim in self.animations.values():
            anim.flip(True, False)

    def get_health(self):
        return self.health

    def get_number_shurikens(self):
        return self.number_shurikens

    def collide(self, x_vel, y_vel):
        """Обработка столкновений с платформами, фруктами, врагами"""
        # Обработка столкновений с платформами
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if x_vel < 0:
                self.rect.left = platform.rect.right
                self.x_vel = 0
            elif x_vel > 0:
                self.rect.right = platform.rect.left
                self.x_vel = 0
            elif y_vel > 0:
                self.on_ground = True
                self.jump = False
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
                self.x_vel = 0
            elif y_vel < 0:
                self.rect.top = platform.rect.bottom
                self.y_vel = 0

    def collide_with_fruits(self):
        # Обработка столкновений с фруктами (взятие фрукта)
        for fruit in fruits_group:
            fruit: Fruit
            if not fruit.is_collected() and pygame.sprite.collide_mask(self,
                                                                       fruit):
                self.health += fruit.get_health()
                print("Жизни героя", self.health)  # для отладки
                fruit.collect()  # Собрать фрукт

    def collide_with_enemies(self):
        # Обработка столкновений с врагами (работает неправильно)
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy: Enemy
            # Имитация головы врага (тестовый вариант)
            enemy_head = pygame.rect.Rect(
                enemy.rect.x + (enemy.rect.width / 4),
                enemy.rect.y, enemy.rect.width / 2,
                enemy.rect.height / 4)

            if self.y_vel > 0 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):
                print('герой наносит урон')
                self.y_vel = -7  # Отскок вверх при прыжке на врага сверху
                self.rect.bottom = enemy.rect.top  # Чтобы не было множественного удара
                enemy.get_hit(self.damage)
                # ...
            # движение по оси X или вверх по оси Y (герой получает урон)
            elif not self.got_hit:  # Если герой не в "шоке"
                self.health -= enemy.get_damage()
                print("Жизни героя", self.health)  # для отладки
                if self.health <= 0:
                    self.defeat()
                    break

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()
                # Изменение векторов скоростей в соответствии со старыми. Было переработано
                if enemy_x_vel < 0 and self.x_vel == 0:
                    self.x_vel = -5
                elif enemy_x_vel > 0 and self.x_vel == 0:
                    self.x_vel = 5
                elif self.direction == 'left':
                    self.x_vel = 5
                elif self.direction == 'right':
                    self.x_vel = -5

                self.y_vel = -5

    def collide_with_spikes(self):
        # Обработка столкновений с шипами
        for spike in spikes_group:
            spike: Spikes
            # Если герой не в "шоке"
            if not self.got_hit and pygame.sprite.collide_mask(self, spike):
                self.health -= spike.get_damage()
                print("Жизни героя", self.health)  # для отладки
                if self.health <= 0:
                    self.defeat()
                    break

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара

                # Изменение векторов скоростей в соответствии со старыми
                if self.x_vel == 0 and self.y_vel > 0:
                    self.x_vel = 0
                elif self.direction == 'right':
                    self.x_vel = -5
                elif self.direction == 'left':
                    self.x_vel = 5

                self.y_vel = -5 if self.y_vel > 0 else 5

    def update(self):
        super().update()

        if not self.health:  # герой повержен
            self.rect.y += 5
            self.animations['stay'].blit(self.image, (0, 0))
            return

        # флаг, нужна ли ещё анимация в текущем обновлении
        flag_anim = True  # нужно, чтобы не было двойной анимации

        if not self.on_ground:
            self.y_vel += GRAVITY
        else:
            self.y_vel = 1
            self.on_ground = False

        self.collide_with_spikes()
        self.collide_with_enemies()
        self.collide_with_fruits()

        self.rect.x += self.x_vel
        self.collide(self.x_vel, 0)

        self.rect.y += self.y_vel
        self.collide(0, self.y_vel)

        # Если игрок попал на шипы,
        # то на протяжении 700 мс проигрывается анимация
        if self.got_hit and pygame.time.get_ticks() - self.got_hit < 700:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return
        else:
            self.got_hit = False  # Анимация прошла
            self.animations['hit'].stop()

        if self.double_jump:
            self.animations['double_jump'].blit(self.image, (0, 0))
            flag_anim = False
            if self.animations['double_jump'].currentFrameNum == \
                    self.animations['double_jump'].numFrames - 1:
                self.double_jump = False

        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_vel = self.speed
            if self.direction == "left":
                self.direction = "right"
                self.flip()
            if flag_anim:
                self.animations['run'].blit(self.image, (0, 0))
                flag_anim = False

        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x_vel = -self.speed

            if self.direction == "right":
                self.direction = "left"
                self.flip()
            if flag_anim:
                self.animations['run'].blit(self.image, (0, 0))
                flag_anim = False

        if flag_anim:  # нет передвижения по оси x
            self.x_vel = 0

        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.on_ground:
                self.on_ground = False
                self.y_vel = -self.height_jump
            if flag_anim:
                self.animations['jump'].blit(self.image, (0, 0))
                flag_anim = False

        if pygame.key.get_pressed()[pygame.K_DOWN]:
            if not self.on_ground:
                self.y_vel = 1.4 * self.height_jump
                if flag_anim:
                    self.animations['fall'].blit(self.image, (0, 0))
                    flag_anim = False

        if pygame.key.get_pressed()[pygame.K_SPACE] \
                and not pygame.key.get_pressed()[pygame.K_DOWN]:
            if self.on_ground:
                self.on_ground = False
                self.y_vel = -1.4 * self.height_jump
                self.double_jump = True
                self.animations['double_jump'].play()
                if flag_anim:
                    self.animations['double_jump'].blit(self.image,
                                                        (0, 0))
                    flag_anim = False

        if pygame.key.get_pressed()[pygame.K_f]:
            self.defeat()

        if flag_anim:  # все клавиши не нажаты
            # Когда клавиши не нажаты и герой на земле, то анимация stay
            if self.on_ground:
                self.animations['stay'].blit(self.image, (0, 0))
            # когда в воздухе и падает анимация падения
            elif self.y_vel >= 0:
                self.animations['fall'].blit(self.image, (0, 0))
            # когда поднимается - анимация прыжка
            else:
                self.animations['jump'].blit(self.image, (0, 0))

    def attack(self):
        """Атака героя"""
        if self.number_shurikens:
            Shuriken(self.rect.right
                     if self.direction == "right" else self.rect.left,
                     self.rect.top, self.direction).move()
            self.number_shurikens -= 1

    def defeat(self):
        """Поражение героя"""
        self.health = 0  # чтобы здоровье не было отрицательным
        self.animations['stay'].flip(False, True)


if __name__ == "__main__":
    running = True
    clock = pygame.time.Clock()

    player, level_x, level_y = load_level('map.txt')

    camera = Camera(level_x, level_y)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # через события, чтобы вылетал один сюрикен
                if event.key == pygame.K_RETURN:
                    player.attack()

        game_screen.fill(pygame.Color("light blue"))
        screen.fill(pygame.Color("black"))

        all_sprites.update()

        if player.health:
            # изменяем ракурс камеры
            camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            game_screen.blit(sprite.image, camera.apply(sprite))

        screen.blit(game_screen, (0, TILE_SIDE))

        font = pygame.font.Font(None, 30)
        text = font.render(f"Жизни: {player.get_health()} Сюрикенов осталось: "
                           f"{player.get_number_shurikens()}",
                           True, (100, 255, 100))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = TILE_SIDE // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
