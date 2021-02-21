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
MAIN_HERO = 'Mask Dude'
# name: (damage, speed, health)
heroes = {'Ninja Frog': hero_parameters(15, 6, 100),
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
            elif elem == '1':
                Checkpoint(
                    x * TILE_SIDE - (TILE_SIDE - Checkpoint.width),
                    y * TILE_SIDE + (TILE_SIDE - Checkpoint.height),
                    'Start')
            elif elem == '9':
                Checkpoint(
                    x * TILE_SIDE - (TILE_SIDE - Checkpoint.width),
                    y * TILE_SIDE + (TILE_SIDE - Checkpoint.height),
                    'End')
            elif elem == '`':
                Saw(x * TILE_SIDE, y * TILE_SIDE)
                # Spikes(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '*':
                Fruit(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '2':
                Backpack(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'b':
                BouncedEnemy(x * TILE_SIDE, y * TILE_SIDE, 10)
            elif elem == 'm':
                Mushroom(x * TILE_SIDE, y * TILE_SIDE, -3.5, 100)
            elif elem == 's':
                Slime(x * TILE_SIDE, y * TILE_SIDE, -1, 100)
            elif elem == 'h':
                Chameleon(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'r':
                Rino(
                    x * TILE_SIDE - (TILE_SIDE - Rino.width),
                    y * TILE_SIDE + (TILE_SIDE - Rino.height)
                )
            elif elem == 'p':
                Plant(
                    x * TILE_SIDE - (TILE_SIDE - Plant.width) + 20,
                    y * TILE_SIDE + (TILE_SIDE - Plant.height), "right"
                )
            elif elem == 'P':
                Plant(
                    x * TILE_SIDE - (TILE_SIDE - Plant.width) + 20,
                    y * TILE_SIDE + (TILE_SIDE - Plant.height), "left"
                )
            elif elem == '@':
                new_player = MainHero(
                    x * TILE_SIDE - (TILE_SIDE - MainHero.width),
                    y * TILE_SIDE + (TILE_SIDE - MainHero.height), MAIN_HERO)

    return new_player, (x + 1) * TILE_SIDE, (y + 1) * TILE_SIDE


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

        self.mask = pygame.mask.from_surface(self.image)

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            f'{name}/Hit.png', 1, 7, anim_delay=100)),

            'jump': pyganim.PygAnimation(cut_sheet(
                f'{name}/Jump.png', 1, 1, anim_delay=100)),

            'double_jump': pyganim.PygAnimation(cut_sheet(
                f'{name}/Double Jump.png', 1, 6, anim_delay=100)),

            'fall': pyganim.PygAnimation(cut_sheet(
                f'{name}/Fall.png', 1, 1, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                f'{name}/Run.png', 1, 12, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                f'{name}/Idle.png', 1, 11, anim_delay=100))
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

    def get_direction(self):
        return self.direction

    def get_hit(self, damage, direction):
        self.health -= damage
        print("Жизни героя", self.health)  # для отладки
        if self.health <= 0:
            self.defeat()

        self.got_hit = pygame.time.get_ticks()  # Время последнего удара
        # Изменение векторов скоростей в соответствии со старыми.
        delta = 5
        if direction == 'left':
            self.x_vel = -delta
        else:
            self.x_vel = delta
        self.y_vel = -5

    def collide(self, x_vel, y_vel):
        """Обработка столкновений с платформами"""
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
        """Обработка столкновений с фруктами (взятие фрукта)"""
        for fruit in fruits_group:
            fruit: Fruit
            if not fruit.is_collected() and pygame.sprite.collide_mask(self,
                                                                       fruit):
                if isinstance(fruit, Backpack):
                    self.number_shurikens += fruit.get_kol()
                else:
                    self.health += fruit.get_health()
                    print("Жизни героя", self.health)  # для отладки
                fruit.collect()  # Собрать фрукт

    def collide_with_checkpoints(self):
        """Обработка столкновений с флажками"""
        for checkpoint in pygame.sprite.spritecollide(self, checkpoints,
                                                      False):
            checkpoint: Checkpoint
            if not checkpoint.moving and checkpoint.get_name() == 'End':
                checkpoint.moving = True
                # уровень пройден

    def collide_with_enemies(self):
        """Обработка столкновений с врагами"""
        for enemy in chameleons:
            enemy_head = pygame.rect.Rect(
                enemy.rect2.x + (enemy.rect2.width / 4),
                enemy.rect2.y, enemy.rect2.width / 2,
                enemy.rect2.height / 4)
            if pygame.rect.Rect.colliderect(self.rect, enemy_head):
                continue
            if pygame.Rect.colliderect(self.rect, enemy.rect):
                enemy.start_attack()
                self.health -= enemy.get_damage()
                print("Жизни героя", self.health)  # для отладки
                if self.health <= 0:
                    self.defeat()
                    break

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()
                self.x_vel = enemy_x_vel * 2
                self.y_vel = -5
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy: Enemy
            # Имитация головы врага (тестовый вариант)
            enemy_head = pygame.rect.Rect(
                enemy.rect.x + (enemy.rect.width / 4),
                enemy.rect.y, enemy.rect.width / 2,
                enemy.rect.height / 4)

            if self.y_vel > 1 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):
                if isinstance(enemy, Chameleon) \
                        and not pygame.Rect.colliderect(self.rect,
                                                        enemy.rect2):
                    continue
                print('герой наносит урон')

                self.y_vel = -7  # Отскок вверх при прыжке на врага сверху
                self.rect.bottom = enemy.rect.top  # Чтобы не было множественного удара
                enemy.get_hit(self.damage)

            # движение по оси X или вверх по оси Y (герой получает урон)
            elif not self.got_hit:  # Если герой не в "шоке"
                if isinstance(enemy, Chameleon):
                    continue
                self.health -= enemy.get_damage()
                print("Жизни героя", self.health)  # для отладки
                if self.health <= 0:
                    self.defeat()
                    break

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()
                # Изменение векторов скоростей в соответствии со старыми.
                delta = 9 if isinstance(enemy, Rino) else 5
                if enemy_x_vel < 0:
                    self.x_vel = -delta
                elif enemy_x_vel > 0:
                    self.x_vel = delta
                self.y_vel = -5

    def collide_with_spikes(self):
        """Обработка столкновений с шипами"""
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
        self.collide_with_checkpoints()

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
            if self.on_ground:
                self.make_dust_particles()

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

    def make_dust_particles(self):
        x = self.rect.bottomright[0] - 9 if self.direction == 'left' \
            else self.rect.bottomleft[0] + 9
        y = self.rect.bottomleft[1] + 2
        Particles(self.direction, (x, y))


if __name__ == "__main__":
    running = True
    pause = False

    clock = pygame.time.Clock()

    player, level_x, level_y = load_level('map.txt')

    camera = Camera(level_x, level_y)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # через события, чтобы вылетал один сюрикен
                if event.key == pygame.K_RETURN and not pause:
                    player.attack()
                elif event.key == pygame.K_p:
                    pause = not pause

        if pause:
            continue

        game_screen.fill(pygame.Color("light blue"))
        screen.fill(pygame.Color("#11A550"))

        all_sprites.update()

        if player.health:
            # изменяем ракурс камеры
            camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            if not issubclass(type(sprite), Enemy):
                game_screen.blit(sprite.image, camera.apply(sprite))

        # рисуем врагов отдельно, чтобы они не были над другими текстурами
        for sprite in enemies_group:
            game_screen.blit(sprite.image, camera.apply(sprite))

        screen.blit(game_screen, (0, TILE_SIDE))

        font = pygame.font.Font(None, 30)
        first = (WIDTH - (50 * 2 + 60 * 2)) // 2
        screen.blit(pygame.transform.scale(load_image('Heart2.png'), (40, 40)),
                    (first, TILE_SIDE // 2 - 20))
        screen.blit(font.render(f": {player.get_health()}",
                                True, (0, 252, 123)),
                    (first + 50, TILE_SIDE // 2 - 10))
        screen.blit(pygame.transform.scale(load_image('stay_shuriken.png', -1),
                                           (36, 36)),
                    (first + 110, TILE_SIDE // 2 - 18))
        screen.blit(font.render(f": {player.get_number_shurikens()}",
                                True, (0, 252, 123)),
                    (first + 160, TILE_SIDE // 2 - 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
