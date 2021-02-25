import os
from random import choice
from collections import namedtuple
from math import ceil
import pygame
import pyganim

from constants import *
from functions import *
from enemy import *
from some_classes import *
from weapon import Shuriken

hero_parameters = namedtuple('hero_parameters', 'damage speed health')
# name: (damage, speed, health)
heroes = {'Ninja Frog': hero_parameters(15, 7, 100),
          'Pink Man': hero_parameters(20, 4, 120),
          'Virtual Guy': hero_parameters(15, 6, 95),
          'Mask Dude': hero_parameters(15, 5, 100)}


class BaseHero(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):

        super().__init__(player_group, all_sprites)
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

        self.number_shurikens = 20  # кол-во оставшихся сюрикенов

        self.transparency = 255
        self.angle = 0
        self.last_speed = self.speed
        self.last_damage = self.damage
        self.boost_duration = 0  # Длительность буста текущего зелья
        # Последний сбор буста. Нужно для вычисления остатка действия зелья
        self.boosts = {'damage': {'boost_duration': 0, 'last_boost': 0,
                                  'effect': self.set_damage},
                       'speed': {'boost_duration': 0, 'last_boost': 0,
                                 'effect': self.set_speed}}
        self.key_up_is_raised = False
        self.is_appeared = False

        self.mask = pygame.mask.from_surface(self.image)

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            f'Heroes/{name}/Hit.png', 1, 7, anim_delay=100)),

            'jump': pyganim.PygAnimation(cut_sheet(
                f'Heroes/{name}/Jump.png', 1, 1, anim_delay=100)),

            'double_jump': pyganim.PygAnimation(cut_sheet(
                f'Heroes/{name}/Double Jump.png', 1, 6, anim_delay=100)),

            'fall': pyganim.PygAnimation(cut_sheet(
                f'Heroes/{name}/Fall.png', 1, 1, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                f'Heroes/{name}/Run.png', 1, 12, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                f'Heroes/{name}/Idle.png', 1, 11, anim_delay=100)),

            'appear': pyganim.PygAnimation(cut_sheet(
                'Appearing.png', 1, 7, anim_delay=100)),

            'disappear': pyganim.PygAnimation(cut_sheet(
                'Disappearing.png', 1, 7, anim_delay=100))}
        for anim in self.animations.values():
            anim.play()

    def flip(self):
        """Разворот всех анимаций"""
        for anim in self.animations.values():
            anim.flip(True, False)

    def get_health(self):
        return self.health

    def get_number_shurikens(self):
        return self.number_shurikens

    def get_direction(self):
        return self.direction

    def collide(self, x_vel, y_vel):
        """Обработка столкновений с платформами"""
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            platform: Platform
            if x_vel < 0:
                self.rect.left = platform.rect.right
                self.x_vel = 0
            elif x_vel > 0:
                self.rect.right = platform.rect.left
                self.x_vel = 0
            elif y_vel > 0:
                if self.y_vel > 1:
                    sound_manager.play_land()

                self.on_ground = True
                self.jump = False
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
                self.x_vel = 0
            elif y_vel < 0:
                self.rect.top = platform.rect.bottom
                self.y_vel = 0

    def collide_with_fruits(self):
        """Обработка столкновений с фруктами и рюкзаком (взятие фрукта)"""
        for fruit in fruits_group:
            fruit: Fruit
            if not fruit.is_collected() and pygame.sprite.collide_mask(self,
                                                                       fruit):
                if isinstance(fruit, Backpack):
                    self.number_shurikens += fruit.get_kol()
                    sound_manager.play_backpack_collected()
                else:
                    self.health += fruit.get_health()
                    sound_manager.play_fruit_collected()
                fruit.collect()  # Собрать фрукт

    def collide_with_potions(self):
        """Обработка столкновений с зельями"""

        for potion in potions_group:
            potion: Potion
            if not potion.is_collected() and pygame.sprite.collide_mask(self,
                                                                        potion):
                name = potion.get_name()

                self.boosts[name]['effect'](potion.get_boost())
                self.boosts[name]['last_boost'] = pygame.time.get_ticks()
                self.boosts[name]['boost_duration'] = potion.get_duration()

                sound_manager.play_potion_collected()

                potion.collect()

    def collide_with_checkpoints(self):
        """Обработка столкновений с флажками"""
        for checkpoint in pygame.sprite.spritecollide(self, checkpoints,
                                                      False):
            checkpoint: Checkpoint
            if checkpoint.get_name() == 'End':
                if not checkpoint.moving:
                    checkpoint.moving = True
                if not list(enemies_group):
                    # уровень пройден
                    print('уровень пройден')

    def collide_with_enemies(self):
        """Обработка столкновений с врагами"""
        for enemy in chameleons:
            if enemy.get_health() <= 0:
                continue
            enemy: Chameleon
            enemy_head = pygame.rect.Rect(
                enemy.rect2.x + (enemy.rect2.width / 4),
                enemy.rect2.y, enemy.rect2.width / 2,
                enemy.rect2.height / 4)
            if self.y_vel > 1 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):
                continue
            if pygame.Rect.colliderect(self.rect, enemy.rect):
                if enemy.get_health() > 0 and not enemy.attack:
                    enemy.start_attack()
            if not self.got_hit and pygame.sprite.collide_mask(self, enemy):
                self.health -= enemy.get_damage()
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()
                    break
                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()
                self.x_vel = enemy_x_vel * 2
                self.y_vel = -5
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy: Enemy
            if enemy.get_health() <= 0:
                continue
            # Имитация головы врага (тестовый вариант)
            enemy_head = pygame.rect.Rect(
                enemy.rect.x + (enemy.rect.width / 5),
                enemy.rect.y, enemy.rect.width / 5 * 3,
                enemy.rect.height / 4)

            if self.y_vel > 1 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):
                if isinstance(enemy, Chameleon) \
                        and not pygame.Rect.colliderect(self.rect,
                                                        enemy.rect2):
                    continue

                self.y_vel = -7  # Отскок вверх при прыжке на врага сверху
                self.rect.bottom = enemy.rect.top  # Чтобы не было множественного удара
                enemy.get_hit(self.damage)

                sound_manager.play_hit()

            # движение по оси X или вверх по оси Y (герой получает урон)
            elif not self.got_hit:  # Если герой не в "шоке"
                if isinstance(enemy, Chameleon):
                    continue
                self.health -= enemy.get_damage()
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()
                    return

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()
                # Изменение векторов скоростей в соответствии со старыми.
                delta = 9 if isinstance(enemy, Rino) else 5
                if enemy_x_vel < 0:
                    self.x_vel = -delta
                elif enemy_x_vel > 0:
                    self.x_vel = delta
                elif self.direction == 'left' and enemy_x_vel == 0:
                    self.x_vel = delta
                elif self.direction == 'right' and enemy_x_vel == 0:
                    self.x_vel = -delta
                self.y_vel = -5

                sound_manager.play_got_hit()

    def collide_with_spikes(self):
        """Обработка столкновений с шипами"""
        for spike in spikes_group:
            spike: Spikes
            # Если герой не в "шоке"
            if not self.got_hit and pygame.sprite.collide_mask(self, spike):
                self.health -= spike.get_damage()
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()
                    return

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара

                # Изменение векторов скоростей в соответствии со старыми
                if self.x_vel == 0 and self.y_vel > 0:
                    self.x_vel = 0
                elif self.direction == 'right':
                    self.x_vel = -5
                elif self.direction == 'left':
                    self.x_vel = 5

                self.y_vel = -5 if self.y_vel > 0 else 5

                sound_manager.play_got_hit()

    def collide_with_bullets(self):
        """Обработка столкновений с пулями (пуля попадает в героя)"""
        for bullet in pygame.sprite.spritecollide(self, bullets_group, True):
            bullet: Bullet
            self.health -= bullet.get_damage()
            if self.health <= 0:
                self.health = 0
                sound_manager.play_game_over()
                return

            self.got_hit = pygame.time.get_ticks()  # Время последнего удара
            # Изменение векторов скоростей в соответствии со старыми.
            delta = 5
            if bullet.get_direction() == 'left':
                self.x_vel = -delta
            else:
                self.x_vel = delta
            self.y_vel = -5

            sound_manager.play_got_hit()

    def update(self):
        super().update()

        # Анимация появления игрока
        if not self.is_appeared:
            self.animations['appear'].play()
            self.animations['appear'].blit(self.image, (0, 0))

            if self.animations['appear'].currentFrameNum + 1 == \
                    self.animations['appear'].numFrames:
                self.is_appeared = True
                self.animations['appear'].stop()
            return

        if not self.health:  # герой повержен
            self.defeat()
            return

        # флаг, нужна ли ещё анимация в текущем обновлении
        flag_anim = True  # нужно, чтобы не было двойной анимации
        now = pygame.time.get_ticks()

        if not self.on_ground:
            self.y_vel += GRAVITY
        else:
            self.y_vel = 1
            self.on_ground = False

        # проверяем столкновения
        self.collide_with_spikes()
        self.collide_with_enemies()
        self.collide_with_fruits()
        self.collide_with_checkpoints()
        self.collide_with_bullets()
        self.collide_with_potions()

        self.rect.x += self.x_vel
        self.collide(self.x_vel, 0)

        self.rect.y += self.y_vel
        self.collide(0, self.y_vel)

        # Если игрок попал на шипы,
        # то на протяжении 700 мс проигрывается анимация
        if self.got_hit and now - self.got_hit < 700:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return
        else:
            self.got_hit = False  # Анимация прошла
            self.animations['hit'].stop()

        for name in self.boosts:
            if self.boosts[name]['last_boost'] and \
                    now - self.boosts[name]['last_boost'] > \
                    self.boosts[name]['boost_duration']:
                self.boosts[name]['effect'](0)
                self.boosts[name]['last_boost'] = 0

        if self.double_jump:
            self.animations['double_jump'].play()  # Начинаем анимацию заново
            self.animations['double_jump'].blit(self.image, (0, 0))
            flag_anim = False
            if self.animations['double_jump'].currentFrameNum == \
                    self.animations['double_jump'].numFrames - 1:
                self.double_jump = False
                self.animations['double_jump'].stop()

        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_vel = self.speed
            if self.direction == "left":
                self.direction = "right"
                self.flip()
            if flag_anim:
                self.animations['run'].blit(self.image, (0, 0))
                flag_anim = False
            if self.on_ground:
                self.make_dust_particles()
                sound_manager.play_move_on_ground()

        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x_vel = -self.speed

            if self.direction == "right":
                self.direction = "left"
                self.flip()
            if flag_anim:
                self.animations['run'].blit(self.image, (0, 0))
                flag_anim = False
            if self.on_ground:
                self.make_dust_particles()
                sound_manager.play_move_on_ground()

        if flag_anim:  # нет передвижения по оси x
            self.x_vel = 0

        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.on_ground:
                self.on_ground = False
                self.y_vel = -self.height_jump
                self.jump = pygame.time.get_ticks()
                # Флаг - отжата ли клавиша "вверх"
                self.key_up_is_raised = False
                sound_manager.play_jump()
            # Если герой не на земле, клавиша вверх отжата,
            # и прошло меньше 1500 мс после прыжка
            elif self.key_up_is_raised and self.jump and now - self.jump < 1500:
                self.double_jump = True
                self.y_vel = -self.height_jump
                self.jump = False
                # Сбрасываем анимацию двойного прыжка
                self.animations['double_jump'].stop()
                sound_manager.play_jump()
        else:
            self.key_up_is_raised = True
        # Если нажата клавиша вниз, то сбивается весь прыжок
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.jump = False
            if not self.on_ground:
                self.y_vel = 1.4 * self.height_jump

        if pygame.key.get_pressed()[pygame.K_SPACE] \
                and not pygame.key.get_pressed()[pygame.K_DOWN]:
            if self.on_ground:
                self.on_ground = False
                self.y_vel = -1.4 * self.height_jump
                self.double_jump = True
                # Сбрасываем анимацию двойного прыжка
                self.animations['double_jump'].stop()
                sound_manager.play_jump()

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
        """Атака героя сюрикеном"""
        if self.number_shurikens:
            Shuriken(self.rect.right - 20
                     if self.direction == "right" else self.rect.left,
                     self.rect.top, self.direction).move()
            self.number_shurikens -= 1

            sound_manager.play_shuriken()

    def defeat(self):
        """Поражение героя"""

        self.x_vel, self.y_vel = 0, 8  # начальная скорость падения

        self.rect = self.rect.move(self.x_vel, self.y_vel)

        frame = self.animations['hit'].getCurrentFrame()
        if self.animations['hit'].currentFrameNum + 1 == \
                self.animations['hit'].numFrames:
            self.animations['hit'].pause()
        else:
            self.animations['hit'].play()

        # Меняем rect при вращении изображения героя
        old_center = self.rect.center
        self.image = pygame.transform.rotate(frame, self.angle)
        self.image.set_alpha(self.transparency)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.angle = (self.angle + 5) % 360  # Угол вращения
        self.transparency -= 5

        # если герой исчезает, то уничтожаем спрайт
        if self.transparency <= 0:
            self.kill()

    def make_dust_particles(self):
        x = self.rect.bottomright[0] - 9 if self.direction == 'left' \
            else self.rect.bottomleft[0] + 9
        y = self.rect.bottomleft[1] + 2
        Particles(self.direction, (x, y))

    def rest_of_boost(self, name) -> str:
        if not self.boosts[name]['last_boost']:
            return '0'
        return str(ceil((self.boosts[name]['boost_duration'] -
                         (pygame.time.get_ticks() - self.boosts[name][
                             'last_boost'])) / 1000))

    def set_speed(self, speedup):
        self.speed = self.last_speed + speedup

    def set_damage(self, delta_damage):
        self.damage = self.last_damage + delta_damage

    def add_paused_time(self, time):
        """Добавление к каждому бусту время паузы"""
        for name in self.boosts:
            self.boosts[name]['last_boost'] += time