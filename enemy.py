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
        # Флаг, на земле ли враг
        self.on_ground = False
        self.health = None  # Здоровье
        self.damage = None  # Урон
        self.got_hit = False  # В "шоке" ли враг
        self.animations = None  # Набор анимаций
        self.transparency = 255  # Прозрачность спрайта
        self.angle = 0  # Угол поворота спрайта
        self.mask = None
        # Максимальное расстояние от точки спавна
        self.max_length = 0

    def update(self):
        self.rect = self.rect.move(0 if self.got_hit else self.x_vel,
                                   self.y_vel)

        # Обновление картинки спрайта врага
        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_hit(self, damage):
        """Получение урона"""

        # Если у врага нет HP, ничего не отнимается больше
        if not self.health:
            return
        self.health -= damage
        self.got_hit = pygame.time.get_ticks()  # Последнее получение урона

        # если враг был в полёте во время удара,
        # то он будет снижаться с начальной скоростью 5
        self.y_vel = 5 if self.y_vel < 0 else self.y_vel
        if self.health <= 0:
            self.health = 0

    def get_damage(self):
        """Получение уроан врага"""

        return self.damage

    def get_position(self):
        """Получение позиции"""

        return self.rect.x, self.rect.y

    def get_x_vel(self):
        """Получение вектора скорости по х"""

        return self.x_vel

    def get_health(self):
        """Получение единиц здоровья"""

        return self.health

    def check_hit(self):
        """Проверка на наличие удара от ГГ"""

        # Если прошло меньше 500 мс после удара, анимация "шока" продолжается
        if self.got_hit and pygame.time.get_ticks() - self.got_hit < 500:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return True

        # Иначе останавливается
        self.animations['hit'].stop()
        self.got_hit = False
        return False

    def defeat(self):
        """Смерть врага"""

        if self.health == 0:
            self.damage = 0  # Обнуляем урон врага
            self.x_vel, self.y_vel = 0, 8  # начальная скорость падения при смерти

            frame = self.animations['hit'].getCurrentFrame()
            # Проигрывание анимации "шока" до конца
            if self.animations['hit'].currentFrameNum + 1 == \
                    self.animations['hit'].numFrames:
                self.animations['hit'].pause()
            else:
                self.animations['hit'].play()

            # Меняем rect и его центр при вращении изображения врага
            old_center = self.rect.center
            self.image = pygame.transform.rotate(frame, self.angle)
            # Установка прозрачности спрайта
            self.image.set_alpha(self.transparency)
            self.rect = self.image.get_rect()
            self.rect.center = old_center  # Обновление центра rect спрайта

            self.angle = (self.angle + 5) % 360  # Угол вращения
            self.transparency -= 5  # Прозрачность уменьшается

            # если враг исчезает, то уничтожается спрайт
            if self.transparency <= 0:
                self.kill()
            return True
        return False


class Bunny(Enemy):
    """Кролик"""

    width, height = 34, 44

    def __init__(self, x, y):
        super().__init__(x + 20, y, Bunny.width, Bunny.height)
        self.jump, self.x_vel, self.y_vel = 10, 0, 0
        self.last_fall = pygame.time.get_ticks()  # Последнее приземление
        self.just_fell = True  # Флаг, только что приземлился
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
            # Если враг соприкоснулся с платформой и вектор скорости по у был больше нуля,
            # значит приземлился на платформу
            if self.y_vel > 0:
                self.on_ground = True  # Приземление на землю
                # низ спрайта становится верхом платформы,
                # по факту их спрайты перестают пересекаться
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
            elif self.y_vel < 0:
                self.rect.top = platform.rect.bottom
                self.y_vel = 0

    def update(self):
        super().update()

        # Если враг мёртв
        if self.defeat():
            return

        self.collide()  # Проверка на коллизии с платформами

        # Проверка на получение удара от ГГ
        if self.check_hit():
            return

        # Проверка, если стоит на земле
        if self.on_ground:
            # Если только что приземлился, включается отсчёт времени на земле
            if self.just_fell:
                self.last_fall = pygame.time.get_ticks()
                self.just_fell = False

            now = pygame.time.get_ticks()  # Время сейчас
            # Прыгает только каждые 3000 мс
            if now - self.last_fall > 3000 and self.jump:
                self.last_fall = now
                self.y_vel = -self.jump
                self.on_ground = False  # Уже не на земле
                self.just_fell = True
            self.animations['stay'].blit(self.image, (0, 0))

        # действие гравитации, если не на земле
        if not self.on_ground:
            self.y_vel += GRAVITY
            # Анимация падения или прыжка в зависимости от направления вектора скорости по у
            if self.y_vel > 0:
                self.animations['fall'].blit(self.image, (0, 0))
            else:
                self.animations['jump'].blit(self.image, (0, 0))

        # Обновление маски
        self.mask = pygame.mask.from_surface(self.image)


class WalkingEnemy(Enemy):
    """Ходячий враг"""

    width, height = 32, 34

    def __init__(self, x_vel, y_vel, max_length, health, damage, x, y, width, height):
        super().__init__(x, y, width, height)
        self.x_vel, self.y_vel = x_vel, y_vel
        # максимальное расстояние от точки спавна
        self.max_length = max_length
        self.health = health  # количество жизней
        self.damage = damage  # урон, который наносит враг при атаке

    def collide(self):
        # если не на земле, то падает, пока не приземлится
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:  # нет соприкосновения с платформой
                self.y_vel += GRAVITY
            else:
                # низ спрайта становится верхом платформы,
                # по факту их спрайты перестают пересекаться
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        # Проверка на все воприкосновения с платформами
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            # Если врезался в стенку, флипаются анимации и меняется направление движения
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
                self.flip()

            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
                self.flip()

    def flip(self):
        """Отзеркаливание всех анимаций по горизонтали"""

        self.x_vel *= -1  # Смена направления движения
        for anim in self.animations.values():
            anim.flip(True, False)

    def update(self):
        super().update()

        if self.defeat():  # Если враг умер
            return

        self.collide()  # Проверка на коллизии с платформами

        if self.check_hit():  # Проверка на получение удара от ГГ
            return

        # Если враг прошёл максимальное расстояние, флипаются все анимации
        if abs(self.rect.x - self.start_x) >= self.max_length:
            self.flip()

        # Анимация ходьбы и стояния в зависимости от вектора скорости по х
        if self.x_vel == 0:
            self.animations['stay'].blit(self.image, (0, 0))
        else:
            self.animations['run'].blit(self.image, (0, 0))

        # Обновление маски спрайта
        self.mask = pygame.mask.from_surface(self.image)


class Chicken(WalkingEnemy):
    """Курица"""

    width, height = 32, 34

    def __init__(self, x, y):
        super().__init__(-3, 0, 200, 25, 15, x, y, WalkingEnemy.width, WalkingEnemy.height)

        # Анимации
        self.animations = {'run': pyganim.PygAnimation(cut_sheet(
            'Enemies/Chicken/Run.png', 1, 14, anim_delay=100)),

            'stay': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chicken/Idle.png', 1, 13, anim_delay=100)),

            'hit': pyganim.PygAnimation(cut_sheet(
                'Enemies/Chicken/Hit.png', 1, 5, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()  # Начало проигрывания всех анимаций


class Mushroom(WalkingEnemy):
    width, height = 32, 32

    def __init__(self, x, y):
        super().__init__(-3.5, 0, 100, 10, 15, x, y, Mushroom.width, Mushroom.height)

        # Анимации
        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Mushroom/Hit.png', 1, 5, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Mushroom/Run.png', 1, 16, anim_delay=100)),

            'stay': pyganim.PygAnimation(
                cut_sheet('Enemies/Mushroom/Idle.png', 1, 14, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()  # Начало проигрывания всех анимаций


class Slime(WalkingEnemy):
    width, height = 44, 30

    def __init__(self, x, y):
        super().__init__(-1, 0, 100, 55, 15, x, y, Slime.width, Slime.height)
        # Анимации
        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/Slime/Hit.png', 1, 5, anim_delay=100)),
            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/Slime/Run.png', 1, 10, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()  # Начало проигрывания всех анимаций


class AngryPig(WalkingEnemy):
    """Злой поросёнок"""

    width, height = 36, 30

    def __init__(self, x, y):
        super().__init__(-2, 0, 200, 65, 10, x, y, AngryPig.width, AngryPig.height)
        self.is_angry = False  # Флаг, ударял ли его главный герой

        self.animations = {'hit': pyganim.PygAnimation(cut_sheet(
            'Enemies/AngryPig/Hit1.png', 1, 5, anim_delay=100)),

            'run': pyganim.PygAnimation(cut_sheet(
                'Enemies/AngryPig/Walk.png', 1, 16, anim_delay=100)),

            'stay': pyganim.PygAnimation(
                cut_sheet('Enemies/AngryPig/Idle.png', 1, 9, anim_delay=100))}

        for anim in self.animations.values():
            anim.play()

    def check_hit(self):
        """Проверка на наличие удара от ГГ"""

        # Проигрывание анимации получения удара 500 мс
        if self.got_hit and pygame.time.get_ticks() - self.got_hit < 500:
            self.animations['hit'].play()
            self.animations['hit'].blit(self.image, (0, 0))
            return True

        if self.got_hit:
            # когда первая hit-анимация, проходит поросёнок становится злым
            self.animations['hit'].stop()
            if not self.is_angry:
                self.is_angry = True
                self.x_vel = 6 if self.x_vel > 0 else -6  # Смена направления
                self.damage = 25  # Увеличение урона
                self.animations['run'] = pyganim.PygAnimation(cut_sheet(
                    'Enemies/AngryPig/Run.png', 1, 12, anim_delay=100))
                self.animations['hit'] = pyganim.PygAnimation(cut_sheet(
                    'Enemies/AngryPig/Hit2.png', 1, 5, anim_delay=100))
                if self.x_vel > 0:  # Флип анимаций в зависимости от направления
                    self.animations['run'].flip(True, False)
                    self.animations['hit'].flip(True, False)
                self.animations['run'].play()
            self.got_hit = False  # Шок проходит
        return False


class Chameleon(Enemy):
    """Хамелеон"""

    def __init__(self, x, y):
        self.width, self.height = 84, 38

        super().__init__(x, y, self.width, self.height)

        chameleons.add(self)

        # Так как ширина изображения хамелеона шире других врагов из-за его языка,
        # происходит отдельного хитбокса для обозначения тела хамелеона
        self.rect2 = pygame.Rect(x + 38, y, 38, 38)

        self.speed = 3  # Скорость
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

        self.prev_x_vel = 0  # Предыдущий вектор скорости по х

        self.attack = False  # Флаг, атакует ли хамелеон

    def start_attack(self):
        """Начинает атаку, если она ещё не идёт"""

        if not self.attack:
            self.attack = True
            return True
        else:
            return False

    def flip(self):
        """Отражение всех анимаций по горизонтали и смена направления"""

        self.x_vel *= -1
        # Так как анимация хамелеона широкая и есть пустое место, то поворачивается с учётом
        # ширины, которая равна высоте
        if self.x_vel > 0:
            self.rect.x += self.width - self.height
        elif self.x_vel < 0:
            self.rect.x -= (self.width - self.height)
        for anim in self.animations.values():
            anim.flip(True, False)

    def collide(self):
        # Хамелеон падает, пока в воздухе
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:
                self.y_vel += GRAVITY
            else:
                # низ спрайта становится верхом платформы,
                # по факту их спрайты перестают пересекаться
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
            # После столкновения с платформой, хамелеон останавливается
            # Сохраняется предыдущий вектор скорости
            self.prev_x_vel = self.x_vel
            self.x_vel = 0

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

        # Хамелеон двигается, если не атакует
        if not self.attack:
            self.rect = self.rect.move(0 if self.got_hit else self.x_vel,
                                       self.y_vel)

        x, y = self.rect.left, self.rect.top
        # Если хамелеон двигался вправо, то анимация также смотрит вправо и хитбокс будет
        # От левого верхнего угла rect, если же влево, то слева в анимации остаётся пустое место,
        # И нужно компенсировать пустоту (x + 38)
        if self.x_vel > 0 or self.x_vel == 0 and self.prev_x_vel > 0:
            self.rect2 = pygame.Rect(x, y, 38, 38)
        else:
            self.rect2 = pygame.Rect(x + 38, y, 38, 38)

        # Хамелеон мёртв
        if self.defeat():
            self.attack = False
            return

        self.collide()

        # Проверка на удар хамелеона персонажем
        if self.check_hit():
            return

        players = list(player_group)
        # В случае, если главный герой жив, хамелеон движется в его сторону
        # Хамелеон знает о расположении ГГ
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

        # Если хамелеон атакует, проигрывается анимация атаки, иначе, если стоит,
        # анимация - стояния, иначе - бега
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
        # Обновление маски спрайта
        self.mask = pygame.mask.from_surface(self.image)


class Rino(Enemy):
    """Носорог"""

    width, height = 52, 34

    def __init__(self, x, y):
        super().__init__(x, y, Rino.width, Rino.height)
        self.speed = 14  # Скорость
        self.x_vel, self.y_vel = -self.speed, 0
        self.prev_x_vel = 0  # Предыдущий вектор скорости по х
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

        # Флаг, ударился ли об стенку носорог
        self.hit_wall = False

        for anim in self.animations.values():
            anim.play()

    def flip(self):
        """Отражение всех анимаций по горизонтали"""

        self.x_vel *= -1
        for anim in self.animations.values():
            anim.flip(True, False)

    def collide(self):
        # если носорог в воздухе, он падает до соприкосновения с платформами
        if not self.on_ground:
            check_on_ground = pygame.sprite.spritecollideany(self, platforms)
            if check_on_ground is None:
                self.y_vel += GRAVITY
            else:
                # низ спрайта становится верхом платформы,
                # по факту их спрайты перестают пересекаться
                self.rect.bottom = check_on_ground.rect.top
                self.y_vel = 0
                self.on_ground = True

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            # Проверка на столкновение со стенкой (платформой)
            if self.x_vel < 0:
                self.rect.left = platform.rect.right

            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
            # начало проигрывания анимации удара об стену
            self.animations['hit_wall'].play()
            self.hit_wall = True  # Флаг удара поднят
            self.prev_x_vel = self.x_vel
            self.x_vel = 0

    def update(self):
        super().update()

        if self.got_hit:  # носорог не останавливается, если его атаковали
            self.rect = self.rect.move(self.x_vel, 0)

        # Носорог мёртв
        if self.defeat():
            return

        # Пока носорог в "шоке" из-за удара об стену, он будет просто стоять
        if not self.hit_wall:
            self.collide()

        # Проверка на удар носорога персонажем
        if self.check_hit():
            return

        if self.hit_wall:
            # анимация удара об стену закончилась
            self.animations['hit_wall'].blit(self.image, (0, 0))
            if self.animations['hit_wall'].currentFrameNum + 1 == \
                    self.animations['hit_wall'].numFrames:
                self.animations['hit_wall'].stop()
                # Удар об стену "закончен"
                self.hit_wall = False
                self.x_vel = self.prev_x_vel
                self.flip()
        elif self.x_vel == 0:
            # Анимация стояния, если скорость по х = 0
            self.animations['stay'].blit(self.image, (0, 0))
        else:
            # Анимация бега
            self.animations['run'].blit(self.image, (0, 0))

        # Обновление маски
        self.mask = pygame.mask.from_surface(self.image)


class Plant(Enemy):
    """Растение"""

    width, height = 44, 42

    def __init__(self, x, y, direction):
        super().__init__(x + 20, y, Plant.width, Plant.height)
        self.x_vel, self.y_vel = 0, 0  # Изначально растение стоит
        self.prev_x_vel = 0
        self.direction = direction  # направление стрельбы
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
        """Отражение всех анимаций по горизонтали"""

        for anim in self.animations.values():
            anim.flip(True, False)

    def start_attack(self):
        """Растение начинает атаку"""

        # Флаг поднят и проигрывается анимация атаки
        self.attack = True
        self.animations['attack'].play()

    def update(self):
        super().update()

        if self.defeat():  # растение мёртво
            return

        if self.check_hit():  # Проверка на удар растения персонажем
            return

        # атака раз в 1300 ms, иначе анимация стояния
        if pygame.time.get_ticks() - self.last_attack > 1300:
            self.start_attack()
        else:
            self.animations['stay'].blit(self.image, (0, 0))

        if self.attack:
            self.animations['attack'].blit(self.image, (0, 0))
            # На пятой анимации атаке выпускается пуля,
            if self.animations['attack'].currentFrameNum == 5 \
                    and not self.bullet_fired:
                self.bullet_fired = True
                # Появление спрайта пули в том направлении, куда смотрит растение
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

        # Обновление спрайта пули
        self.mask = pygame.mask.from_surface(self.image)
