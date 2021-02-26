import pyganim

from functions import *
from weapon import Bullet


class Enemy(pygame.sprite.Sprite):
    """Базовый класс врага"""
    def __init__(self, x, y, width, height):
        super().__init__(enemies_group, all_sprites)

        self.width, self.height = width, height

        self.start_x, self.start_y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height))
        self.x_vel, self.y_vel = None, None
        self.on_ground = False
        self.health = None
        self.damage = None
        self.got_hit = False
        self.animations = None
        self.transparency = 255
        self.angle = 0
        self.mask = None
        self.max_length = 0

    def update(self):
        self.rect = self.rect.move(0 if self.got_hit else self.x_vel,
                                   self.y_vel)

        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_hit(self, damage):
        if not self.health:
            return
        self.health -= damage
        self.got_hit = pygame.time.get_ticks()

        # если враг был в полёте во время удара,
        # то он будет снижаться с начальной скоростью 5
        self.y_vel = 5 if self.y_vel < 0 else self.y_vel
        if self.health <= 0:
            self.health = 0

    def get_damage(self):
        return self.damage

    def get_position(self):
        return self.rect.x, self.rect.y

    def get_x_vel(self):
        return self.x_vel

    def get_health(self):
        return self.health

    def check_hit(self):
        """Проверка на наличие удара от ГГ"""

        if self.got_hit and pygame.time.get_ticks() - self.got_hit < 500:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return True

        self.animations['hit'].stop()
        self.got_hit = False
        return False

    def defeat(self):
        """Смерть врага"""

        if self.health == 0:
            self.damage = 0
            self.x_vel, self.y_vel = 0, 8  # начальная скорость падения

            frame = self.animations['hit'].getCurrentFrame()
            if self.animations['hit'].currentFrameNum + 1 == \
                    self.animations['hit'].numFrames:
                self.animations['hit'].pause()
            else:
                self.animations['hit'].play()

            # Меняем rect при вращении изображения врага
            old_center = self.rect.center
            self.image = pygame.transform.rotate(frame, self.angle)
            self.image.set_alpha(self.transparency)
            self.rect = self.image.get_rect()
            self.rect.center = old_center

            self.angle = (self.angle + 5) % 360  # Угол вращения
            self.transparency -= 5

            # если враг исчезает, то уничтожаем спрайт
            if self.transparency <= 0:
                self.kill()
            return True
        return False


class Bunny(Enemy):
    width, height = 34, 44

    def __init__(self, x, y, jump):
        super().__init__(x, y, Bunny.width, Bunny.height)
        self.jump, self.x_vel, self.y_vel = jump, 0, 0
        self.last_fall = pygame.time.get_ticks()
        self.just_fell = True
        self.health = 45  # количество жизней
        self.damage = 15  # урон, который наносит враг при атаке

        self.animations = {'jump': pyganim.PygAnimation(cut_sheet(
            'Enemies/Bunny/Jump.png', 1, 1, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Bunny/Idle.png', 1, 8, anim_delay=100)),

            'fall': pyganim.PygAnimation(cut_sheet(
                'Enemies/Bunny/Fall.png', 1, 1, anim_delay=100)),

            'hit': pyganim.PygAnimation(cut_sheet(
                'Enemies/Bunny/Hit.png', 1, 5, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()

    def collide(self):
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.y_vel > 0:
                self.on_ground = True
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
            elif self.y_vel < 0:
                self.rect.top = platform.rect.bottom
                self.y_vel = 0

    def update(self):
        super().update()

        if self.defeat():
            return

        self.collide()

        if self.check_hit():
            return

        if self.on_ground:
            if self.just_fell:
                self.last_fall = pygame.time.get_ticks()
                self.just_fell = False

            now = pygame.time.get_ticks()
            if now - self.last_fall > 3000 and self.jump:
                self.last_fall = now
                self.y_vel = -self.jump
                self.on_ground = False
                self.just_fell = True
            self.animations['stay'].blit(self.image, (0, 0))

        if not self.on_ground:
            self.y_vel += GRAVITY
            if self.y_vel > 0:
                self.animations['fall'].blit(self.image, (0, 0))
            else:
                self.animations['jump'].blit(self.image, (0, 0))

        self.mask = pygame.mask.from_surface(self.image)


class WalkingEnemy(Enemy):
    width, height = 32, 34

    def collide(self):
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:
                self.y_vel += GRAVITY
            else:
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
                self.flip()

            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
                self.flip()

    def flip(self):
        self.x_vel *= -1
        for anim in self.animations.values():
            anim.flip(True, False)

    def update(self):
        super().update()

        if self.defeat():
            return

        self.collide()

        if self.check_hit():
            return

        if abs(self.rect.x - self.start_x) >= self.max_length:
            self.flip()

        if self.x_vel == 0:
            self.animations['stay'].blit(self.image, (0, 0))
        else:
            self.animations['run'].blit(self.image, (0, 0))

        self.mask = pygame.mask.from_surface(self.image)


class Chicken(WalkingEnemy):
    width, height = 32, 34

    def __init__(self, x, y):
        super().__init__(x, y, WalkingEnemy.width, WalkingEnemy.height)
        speed, max_length = 3, 200
        self.x_vel, self.y_vel = -speed, 0
        self.max_length = max_length
        self.health = 25  # количество жизней
        self.damage = 15  # урон, который наносит враг при атаке

        self.animations = {'run': pyganim.PygAnimation(cut_sheet(
            'Enemies/Chicken/Run.png', 1, 14, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chicken/Idle.png', 1, 13, anim_delay=100)),

            'hit': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chicken/Hit.png', 1, 5, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()


class Mushroom(WalkingEnemy):
    width, height = 32, 32

    def __init__(self, x, y, speed, max_length):
        super().__init__(x, y, Mushroom.width, Mushroom.height)
        self.x_vel, self.y_vel = speed, 0
        self.max_length = max_length
        self.health = 10  # количество жизней
        self.damage = 15  # урон, который наносит враг при атаке

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Mushroom/Hit.png', 1, 5, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Mushroom/Run.png', 1, 16, anim_delay=100)),

            'stay': pyganim.PygAnimation(
                cut_sheet('Enemies/Mushroom/Idle.png', 1, 14, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()


class Slime(WalkingEnemy):
    width, height = 44, 30

    def __init__(self, x, y, speed, max_length):
        super().__init__(x, y, Slime.width, Slime.height)
        self.x_vel, self.y_vel = speed, 0
        self.max_length = max_length
        self.health = 55  # количество жизней
        self.damage = 15  # урон, который наносит враг при атаке

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Slime/Hit.png', 1, 5, anim_delay=100)),
            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Slime/Run.png', 1, 10, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()


class AngryPig(WalkingEnemy):
    width, height = 36, 30

    def __init__(self, x, y):
        super().__init__(x, y, AngryPig.width, AngryPig.height)
        speed, max_length = 2, 200
        self.x_vel, self.y_vel = -speed, 0
        self.max_length = max_length
        self.health = 65  # количество жизней
        self.damage = 10  # урон, который наносит враг при атаке
        self.is_angry = False

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/AngryPig/Hit1.png', 1, 5, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/AngryPig/Walk.png', 1, 16, anim_delay=100)),

            'stay': pyganim.PygAnimation(
                cut_sheet('Enemies/AngryPig/Idle.png', 1, 9, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()

    def check_hit(self):
        # Проверка на наличие удара от ГГ

        if self.got_hit and pygame.time.get_ticks() - self.got_hit < 500:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return True

        if self.got_hit:
            # когда первая hit-анимация, проходит поросёнок становится злым
            self.animations['hit'].stop()
            if not self.is_angry:
                self.is_angry = True
                self.x_vel = 6 if self.x_vel > 0 else -6
                self.damage = 25
                self.animations['run'] = pyganim.PygAnimation(cut_sheet(
                    'Enemies/AngryPig/Run.png', 1, 12, anim_delay=100))
                self.animations['hit'] = pyganim.PygAnimation(cut_sheet(
                    'Enemies/AngryPig/Hit2.png', 1, 5, anim_delay=100))
                if self.x_vel > 0:
                    self.animations['run'].flip(True, False)
                    self.animations['hit'].flip(True, False)
                self.animations['run'].play()
            self.got_hit = False
        return False


class Chameleon(Enemy):
    def __init__(self, x, y):
        self.width, self.height = 84, 38
        super().__init__(x, y, self.width, self.height)

        chameleons.add(self)
        self.rect2 = pygame.Rect(x + 38, y, 38, 38)

        self.speed = 3
        self.x_vel, self.y_vel = -self.speed, 0

        self.health = 50  # количество жизней
        self.damage = 25  # урон, который наносит враг при атаке

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Chameleon/Hit.png', 1, 5, anim_delay=100)),

            'attack': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chameleon/Attack.png', 1, 10, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chameleon/Run.png', 1, 8, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chameleon/Idle.png', 1, 13, anim_delay=100))
        }
        for anim in self.animations.values():
            anim.play()

        self.prev_x_vel = 0

        self.attack = False

    def start_attack(self):
        """Начинает атаку, если она ещё не идёт"""
        if not self.attack:
            self.attack = True
            return True
        else:
            return False

    def flip(self):
        self.x_vel *= -1
        if self.x_vel > 0:
            self.rect.x += self.width - self.height
        elif self.x_vel < 0:
            self.rect.x -= (self.width - self.height)
        for anim in self.animations.values():
            anim.flip(True, False)

    def collide(self):
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:
                self.y_vel += GRAVITY
            else:
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
            self.prev_x_vel = self.x_vel
            self.x_vel = 0

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

        if not self.attack:
            self.rect = self.rect.move(0 if self.got_hit else self.x_vel,
                                       self.y_vel)

        x, y = self.rect.left, self.rect.top
        if self.x_vel > 0 or self.x_vel == 0 and self.prev_x_vel > 0:
            self.rect2 = pygame.Rect(x, y, 38, 38)
        else:
            self.rect2 = pygame.Rect(x + 38, y, 38, 38)

        if self.defeat():
            self.attack = False
            return

        self.collide()

        if self.check_hit():
            return

        players = list(player_group)
        if players:
            player = players[0]
            if self.x_vel >= 0 and \
                    self.rect.left > player.rect.right \
                    and self.prev_x_vel >= 0 or \
                    self.x_vel <= 0 and \
                    self.rect.right < player.rect.left \
                    and self.prev_x_vel <= 0:
                if self.x_vel == 0:
                    self.x_vel = self.prev_x_vel
                    self.prev_x_vel = 0
                self.flip()

        if self.attack:
            self.animations['attack'].play()
            self.animations['attack'].blit(self.image, (0, 0))
        elif self.x_vel == 0:
            self.animations['stay'].blit(self.image, (0, 0))
            self.animations['attack'].stop()
        else:
            self.animations['run'].blit(self.image, (0, 0))
            self.animations['attack'].stop()

        # анимация атаки закончилась
        if self.attack and \
                self.animations['attack'].currentFrameNum + 1 == \
                self.animations['attack'].numFrames:
            self.attack = False

        self.mask = pygame.mask.from_surface(self.image)


class Rino(Enemy):
    width, height = 52, 34

    def __init__(self, x, y):
        super().__init__(x, y, Rino.width, Rino.height)
        speed = 14
        self.x_vel, self.y_vel = -speed, 0
        self.prev_x_vel = 0
        self.health = 65  # количество жизней
        self.damage = 25  # урон, который наносит враг при атаке

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Rino/Hit.png', 1, 5, anim_delay=100)),

            'hit_wall': pyganim.PygAnimation(cut_sheet(
                'Enemies/Rino/Hit Wall.png', 1, 4, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Rino/Run.png', 1, 6, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Rino/Idle.png', 1, 11, anim_delay=100))
        }

        self.hit_wall = False

        for anim in self.animations.values():
            anim.play()

    def flip(self):
        self.x_vel *= -1
        for anim in self.animations.values():
            anim.flip(True, False)

    def collide(self):
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:
                self.y_vel += GRAVITY
            else:
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.x_vel < 0:
                self.rect.left = platform.rect.right

            elif self.x_vel > 0:
                self.rect.right = platform.rect.left

            self.animations['hit_wall'].play()
            self.hit_wall = True
            self.prev_x_vel = self.x_vel
            self.x_vel = 0

    def update(self):
        super().update()

        if self.got_hit:  # носорог не останавливается, если его атаковали
            self.rect = self.rect.move(self.x_vel, 0)

        if self.defeat():
            return

        if not self.hit_wall:
            self.collide()

        if self.check_hit():
            return

        if self.hit_wall:
            # анимация удара об стену закончилась
            self.animations['hit_wall'].blit(self.image, (0, 0))
            if self.animations['hit_wall'].currentFrameNum + 1 == \
                    self.animations['hit_wall'].numFrames:
                self.animations['hit_wall'].stop()
                self.hit_wall = False
                self.x_vel = self.prev_x_vel
                self.flip()
        elif self.x_vel == 0:
            self.animations['stay'].blit(self.image, (0, 0))
        else:
            self.animations['run'].blit(self.image, (0, 0))

        self.mask = pygame.mask.from_surface(self.image)


class Plant(Enemy):
    width, height = 44, 42

    def __init__(self, x, y, direction):
        super().__init__(x, y, Plant.width, Plant.height)
        self.x_vel, self.y_vel = 0, 0
        self.prev_x_vel = 0
        self.direction = direction
        self.health = 65  # количество жизней
        self.damage = 25  # урон, который наносит враг при атаке

        self.last_attack = pygame.time.get_ticks()  # Время последнего удара

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Plant/Hit.png', 1, 5, anim_delay=100)),

            'attack': pyganim.PygAnimation(cut_sheet(
                'Enemies/Plant/Attack.png', 1, 8, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Plant/Idle.png', 1, 11, anim_delay=100))
        }

        if self.direction == "right":
            self.flip()

        self.attack = False  # идёт ли сейчас атака
        self.bullet_fired = False  # выпущена ли пуля на текущей атаке

        self.animations['stay'].play()

    def flip(self):
        for anim in self.animations.values():
            anim.flip(True, False)

    def start_attack(self):
        """Растение начинает атаку"""
        self.attack = True
        self.animations['attack'].play()

    def update(self):
        super().update()

        if self.defeat():
            return

        if self.check_hit():
            return

        # атака раз в 1300 ms
        if pygame.time.get_ticks() - self.last_attack > 1300:
            self.start_attack()
        else:
            self.animations['stay'].blit(self.image, (0, 0))

        if self.attack:
            self.animations['attack'].blit(self.image, (0, 0))
            # На пятой анимации атаки выпускается пуля
            if self.animations['attack'].currentFrameNum == 5 \
                    and not self.bullet_fired:
                self.bullet_fired = True
                Bullet(self.rect.right
                       if self.direction == "right" else self.rect.left,
                       self.rect.top + 6, self.direction).move()
            # анимация атаки закончилась
            if self.animations['attack'].currentFrameNum + 1 == \
                    self.animations['attack'].numFrames:
                self.animations['attack'].stop()
                self.attack = False
                self.bullet_fired = False
                # Атака закончилась - выстрел пули прекратился
                # Время начинает отсчитываться именно тогда, когда атака закончилась
                self.last_attack = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

