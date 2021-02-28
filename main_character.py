from math import ceil

from enemy import *
from some_classes import *
from weapon import Shuriken


class BaseHero(pygame.sprite.Sprite):
    """Базовый класс главного героя"""

    def __init__(self, x, y, width, height):
        # На данный момент всего один ГГ,
        # но планируется добавить ещё несколько с разной механикой
        # На этот случай нужен базовый класс главного героя
        super().__init__(player_group, all_sprites)
        self.width, self.height = width, height

        self.start_x, self.start_y = x, y  # Начальные координаты левого верхнего угла
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height))
        self.x_vel, self.y_vel = None, None
        self.on_ground = False  # флаг, на земле ли

    def update(self):
        """Обновление спрайта"""

        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_position(self):
        """Получение координат героя"""

        return self.rect.x, self.rect.y


class MainHero(BaseHero):
    width, height = 32, 32

    def __init__(self, x, y, name):
        super().__init__(x, y, MainHero.width, MainHero.height)
        self.direction = "right"  # Направление движения героя на данный момент
        self.speed = HEROES[name].speed
        self.jump, self.x_vel, self.y_vel = 0, 0, 0
        self.height_jump = 10  # показатель высоты прыжка
        self.double_jump = False  # происходит ли сейчас двойной прыжок
        self.got_hit = False  # Время последнего удара
        self.health = HEROES[name].health  # количество жизней
        # урон, который наносит герой при напрыгивании на врага
        self.damage = HEROES[name].damage

        self.number_shurikens = 20  # кол-во оставшихся сюрикенов

        self.win = False   # прошёл ли герой текущий уровень

        self.transparency = 255  # Прозрачность спрайта
        self.angle = 0  # Угол поворота спрайта (нужен для анимации смерти)
        self.last_speed = self.speed
        self.last_damage = self.damage
        self.boost_duration = 0  # Длительность буста текущего зелья

        # Хранения информации о бустах, в виде JSON
        # Время последнего сбора буста (last_boost), нужно для вычисления остатка действия зелья
        # boost_duration - время действия буста
        # effect - метод, который изменяет параметры ГГ
        self.boosts = {'damage': {'boost_duration': 0, 'last_boost': 0,
                                  'effect': self.set_damage},
                       'speed': {'boost_duration': 0, 'last_boost': 0,
                                 'effect': self.set_speed}}

        # флаг, когда поднята клавиша стрелки вверх, нужен для двойного прыжка
        self.key_up_is_raised = False
        self.is_appeared = False  # Появился ли герой в начале игры (перед этим анимация появления)

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
        """Получение единиц здоровья"""

        return self.health

    def get_number_shurikens(self):
        """Получение кол-ва оставшихся сюрикенов"""

        return self.number_shurikens

    def get_direction(self):
        """Получение актуального направления"""

        return self.direction

    def is_win(self):
        """Получение состояния прохождения уровня героем"""

        return self.win

    def collide(self, x_vel, y_vel):
        """Обработка столкновений с платформами"""

        for platform in pygame.sprite.spritecollide(self, platforms, False):
            platform: Platform

            if x_vel < 0:  # Столкновение со стенкой слева
                self.rect.left = platform.rect.right
                self.x_vel = 0

            elif x_vel > 0:  # Столкновение со стенкой справа
                self.rect.right = platform.rect.left
                self.x_vel = 0

            elif y_vel > 0:  # Столкновение с платформой снизу (приземление)
                # проигрывание звука приземления
                if self.y_vel > 1:
                    sound_manager.play_land()

                self.on_ground = True
                self.jump = False
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
                self.x_vel = 0

            elif y_vel < 0:  # Столкновение с платформой сверху
                self.rect.top = platform.rect.bottom
                self.y_vel = 0

    def collide_with_fruits(self):
        """Обработка столкновений с фруктами (взятие фрукта)"""

        for fruit in fruits_group:
            fruit: Fruit
            # Если фрукт еще не собран и спрайт героя пересекается с фруктом по маске
            if not fruit.is_collected() and pygame.sprite.collide_mask(self, fruit):
                self.health += fruit.get_health()  # Фрукт прибавляет здоровье
                fruit.collect()  # Собрать фрукт
                sound_manager.play_fruit_collected()  # Проигрывание звука собранного фрукта

    def collide_with_backpacks(self):
        """Обработка столкновений с рюкзаками (взятие фрукта)"""

        for backpack in backpacks_group:
            backpack: Backpack
            # Если рюкзак еще не собран и спрайт героя пересекается с рюкзаком по маске
            if not backpack.is_collected() and pygame.sprite.collide_mask(self, backpack):
                self.number_shurikens += backpack.get_kol()  # Рюкзак прибавляет сюрикены
                backpack.collect()  # Собрать рюкзак
                sound_manager.play_backpack_collected()  # Проигрывание звука собранного рюкзака

    def collide_with_potions(self):
        """Обработка столкновений с зельями"""

        for potion in potions_group:
            potion: Potion
            # Если зелье еще не собрано и спрайт героя пересекается с зельем по маске
            if not potion.is_collected() and pygame.sprite.collide_mask(self,
                                                                        potion):
                name = potion.get_name()  # Получение типа зелья: скорости или урона

                # Изменение параметров ГГ (effect), начало отсчёта времени (last_boost)
                # И получение длительности действия зелья
                self.boosts[name]['effect'](potion.get_boost())
                self.boosts[name]['last_boost'] = pygame.time.get_ticks()
                self.boosts[name]['boost_duration'] = potion.get_duration()

                sound_manager.play_potion_collected()  # Проигрывание звука собранного зелья

                potion.collect()  # Собрать зелье

    def collide_with_checkpoints(self):
        """Обработка столкновений с флажками"""

        for checkpoint in pygame.sprite.spritecollide(self, checkpoints,
                                                      False):
            checkpoint: Checkpoint
            # Если тип чекпоинта "End", значит, герой добрался до финиша.
            if checkpoint.get_name() == 'End':
                if not checkpoint.moving:
                    checkpoint.moving = True
                if not list(enemies_group):
                    # уровень пройден
                    self.win = True

    def collide_with_enemies(self):
        """Обработка столкновений с врагами"""

        # Сначала обрабатываются столкновения с хамелеонами, так как у них особая механика
        for enemy in chameleons:
            if enemy.get_health() <= 0:  # если же у хамелеона HP <= 0 пропускаем его
                continue
            enemy: Chameleon
            # Искусственно добавляем хитбокс головы хамелеона
            # 3 / 5 в длину и 1 пиксель в высоту
            enemy_head = pygame.rect.Rect(
                enemy.rect2.x + (enemy.rect2.width / 5),
                enemy.rect2.y, enemy.rect2.width / 5 * 3, 1)

            # Если герой падает сверху и сталкивается с головой хамелеона,
            # то обработка пропускается, так как она будет дальше
            if self.y_vel > 1 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):
                continue

            # Если главный герой столкнулся не только с телом хамелеона, а и ещё с зоной его атаки
            # то хамелеон начинает атаковать, если ещё не атакует
            if pygame.Rect.colliderect(self.rect, enemy.rect):
                if enemy.get_health() > 0 and not enemy.attack:
                    enemy.start_attack()

            # Если герой во время атаки хамелеона не в шоке и всё еще соприкасается с хамелеоном,
            # то ГГ получает урон
            if not self.got_hit and pygame.sprite.collide_mask(self, enemy):
                self.health -= enemy.get_damage()
                # если после удара у ГГ не осталось здоровья, прохождение уровня завершено
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()  # проигрывание мелодии поражения
                    break

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара героя врагом
                enemy_x_vel = enemy.get_x_vel()  # Направление скорости врага
                self.x_vel = enemy_x_vel * 2  # Герой летит в ту сторону, куда двигался враг
                self.y_vel = -5  # Отлёт по у
                sound_manager.play_got_hit()  # Проигрывание звука получения удара

        # Столкновения со всеми врагами
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy: Enemy
            if enemy.get_health() <= 0:
                continue
            # Искусственно добавляем хитбокс головы хамелеона
            # 3 / 5 в длину и 1 пиксель в высоту
            enemy_head = pygame.rect.Rect(
                enemy.rect.x + (enemy.rect.width / 5),
                enemy.rect.y, enemy.rect.width / 5 * 3, 1)

            # Если герой падает сверху и сталкивается с головой врага
            if self.y_vel > 1 and pygame.rect.Rect.colliderect(self.rect,
                                                               enemy_head):

                # Если этим врагом был хамелеон и враг не упал именно на голову хамелеона (rect2)
                if isinstance(enemy, Chameleon) \
                        and not pygame.Rect.colliderect(self.rect,
                                                        enemy.rect2):
                    continue

                self.y_vel = -7  # Отскок вверх при прыжке на врага сверху
                self.rect.bottom = enemy.rect.top  # Чтобы не было множественного удара
                enemy.get_hit(self.damage)  # Враг получает урон

                sound_manager.play_hit()  # Проигрывание звука удара

            # движение по оси X или вверх по оси Y (герой получает урон)
            elif not self.got_hit:  # Если герой не в "шоке"
                # Если это не хамелеон, так как обработка удара хамелеона была ранее, пропускаем
                if isinstance(enemy, Chameleon):
                    continue
                # если враг и ГГ не пересекаются по маске, пропускаем
                if not pygame.sprite.collide_mask(self, enemy):
                    continue
                self.health -= enemy.get_damage()  # получение урона от врага
                # Если после удара, не осталось здоровья у главного персонажа, игра проиграна и
                # проигрывается мелодия проигрыша
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()
                    return

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара
                enemy_x_vel = enemy.get_x_vel()  # Направление скорости врага
                # Изменение векторов скоростей в соответствии со старыми.

                # Если удар был с носорогом, ГГ отлетает с большей скоростью по х
                delta = 9 if isinstance(enemy, Rino) else 5

                # Выбор направления отлёта в зависимости от скорости движения врага
                if enemy_x_vel < 0:
                    self.x_vel = -delta
                elif enemy_x_vel > 0:
                    self.x_vel = delta
                elif self.direction == 'left' and enemy_x_vel == 0:
                    self.x_vel = delta
                elif self.direction == 'right' and enemy_x_vel == 0:
                    self.x_vel = -delta
                self.y_vel = -5  # Отскок вверх при столкновении с врагом

                sound_manager.play_got_hit()  # проигрывание звука получения урона

    def collide_with_spikes(self):
        """Обработка столкновений с шипами"""

        for spike in spikes_group:
            spike: Spikes
            # Если герой не в "шоке" и пересекается по маске с шипами
            if not self.got_hit and pygame.sprite.collide_mask(self, spike):
                self.health -= spike.get_damage()  # герой получает урон
                if self.health <= 0:
                    self.health = 0
                    sound_manager.play_game_over()  # если нет здоровья, уровень проигран
                    return

                self.got_hit = pygame.time.get_ticks()  # Время последнего удара

                # Изменение векторов скоростей в соответствии со старыми
                if self.x_vel == 0 and self.y_vel > 0:
                    self.x_vel = 0
                elif self.direction == 'right':
                    self.x_vel = -5
                elif self.direction == 'left':
                    self.x_vel = 5

                # Отскок по у в зависимости от направления скорости по у
                self.y_vel = -5 if self.y_vel > 0 else 5

                sound_manager.play_got_hit()  # проигрывание звука получения удара

    def collide_with_bullets(self):
        """Обработка столкновений с пулями (пуля попадает в героя)"""

        for bullet in pygame.sprite.spritecollide(self, bullets_group, True):
            bullet: Bullet
            self.health -= bullet.get_damage()  # Получение урона во всяком случае
            if self.health <= 0:
                self.health = 0
                sound_manager.play_game_over()  # если не осталось здоровья, уровень проигран
                return

            self.got_hit = pygame.time.get_ticks()  # Время последнего удара
            # Изменение векторов скоростей в соответствии со старыми.
            delta = 5
            if bullet.get_direction() == 'left':
                self.x_vel = -delta
            else:
                self.x_vel = delta
            self.y_vel = -5  # Отскок вверх по у

            sound_manager.play_got_hit()  # проигрывание звука получения удара

    def update(self):
        super().update()

        # Анимация появления игрока, если ещё не появился (is_appeared)
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
        now = pygame.time.get_ticks()  # Время на момент обновления спрайта персонажа

        if not self.on_ground:
            # Действие гравитации, если не на земле
            self.y_vel += GRAVITY
        else:
            # если герой на земле, то падает вниз со скоростью 1
            # это нужно, чтобы он не зависал в воздухе, когда сходил с платформ
            self.y_vel = 1
            self.on_ground = False

        # проверяем столкновения
        self.collide_with_spikes()  # с шипами
        self.collide_with_enemies()  # с врагами
        self.collide_with_fruits()  # с фруктами
        self.collide_with_backpacks()  # с рюкзаками
        self.collide_with_checkpoints()  # с чекпоинтами
        self.collide_with_bullets()  # с пулями
        self.collide_with_potions()  # с зельями

        # Проверка на столкновения с платформами, причём по каждой из оси координат - так удобнее
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

        # Если прошло время действия зелья, возвращаем параметры ГГ обратно
        for name in self.boosts:
            if self.boosts[name]['last_boost'] and \
                    now - self.boosts[name]['last_boost'] > \
                    self.boosts[name]['boost_duration']:
                self.boosts[name]['effect'](0)
                self.boosts[name]['last_boost'] = 0

        # Если был нажат двойной прыжок, то проигрываетс соответствующая анимация
        if self.double_jump:
            self.animations['double_jump'].play()  # Начинаем анимацию заново
            self.animations['double_jump'].blit(self.image, (0, 0))
            flag_anim = False
            # Анимация кончилась
            if self.animations['double_jump'].currentFrameNum == \
                    self.animations['double_jump'].numFrames - 1:
                self.double_jump = False
                self.animations['double_jump'].stop()

        # Нажата клавиша стрелки вправо
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_vel = self.speed
            # флипаем анимацию в нужное время
            if self.direction == "left":
                self.direction = "right"
                self.flip()
            if flag_anim:
                self.animations['run'].blit(self.image, (0, 0))
                flag_anim = False  # Анимация больше не нужна на этом обновлении
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

        if flag_anim:  # нет передвижения по оси x, тогда скорость по х обнуляется
            self.x_vel = 0

        # Нажата клавиша стрелки вверх
        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.on_ground:
                # Если гг был на земле
                self.on_ground = False
                self.y_vel = -self.height_jump  # скорость по у равна скорости прыжка
                self.jump = pygame.time.get_ticks()  # Время последнего прыжка
                # Флаг - отжата ли клавиша "вверх"
                # Клавиша вверх становится не отжатой (нужно для двойного прыжка)
                self.key_up_is_raised = False
                sound_manager.play_jump()  # Звук прыжка
            # Если герой не на земле, клавиша вверх отжата,
            # и прошло меньше 1500 мс после прыжка, тогда герой подпрыгивает в воздухе еще раз
            elif self.key_up_is_raised and self.jump and now - self.jump < 1500:
                self.double_jump = True
                self.y_vel = -self.height_jump
                self.jump = False
                # Сбрасываем анимацию двойного прыжка
                self.animations['double_jump'].stop()
                sound_manager.play_jump()  # звук прыжка
        else:
            # если же была нажата клавиша отлична от стрелки вверх,
            # то клавиша вверх становится отжатой
            self.key_up_is_raised = True
        # Если нажата клавиша вниз, то сбивается весь прыжок
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.jump = False
            if not self.on_ground:  # И герой падает с большим ускорением вниз
                self.y_vel = 1.4 * self.height_jump

        # нажата клавиша стрелки вверх и не нажата в это время стрелка вниз, то происохдит
        if pygame.key.get_pressed()[pygame.K_SPACE] \
                and not pygame.key.get_pressed()[pygame.K_DOWN]:
            if self.on_ground:
                self.on_ground = False  # Герой оказывается не на земле
                self.y_vel = -1.4 * self.height_jump  # Подскок вверх
                self.double_jump = True  #
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

        # Если сюрикены вообще имеются
        if self.number_shurikens:
            # Появляется спрайт сюрикена
            Shuriken(self.rect.right - 20
                     if self.direction == "right" else self.rect.left,
                     self.rect.top, self.direction).move()
            self.number_shurikens -= 1

            sound_manager.play_shuriken()  # звук вылета сюрикена

    def defeat(self):
        """Поражение героя"""

        self.x_vel, self.y_vel = 0, 8  # начальная скорость падения

        self.rect = self.rect.move(self.x_vel, self.y_vel)

        # Начинаем анимацию получения урона
        frame = self.animations['hit'].getCurrentFrame()
        if self.animations['hit'].currentFrameNum + 1 == \
                self.animations['hit'].numFrames:
            self.animations['hit'].pause()  # анимация завершилась
        else:
            self.animations['hit'].play()

        # Меняем rect при вращении изображения героя
        old_center = self.rect.center
        self.image = pygame.transform.rotate(frame, self.angle)
        self.image.set_alpha(self.transparency)  # уменьшение прозрачности
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        self.angle = (self.angle + 5) % 360  # Угол вращения
        self.transparency -= 5

        # если герой исчезает, то уничтожаем спрайт
        if self.transparency <= 0:
            self.kill()

    def make_dust_particles(self):
        """Создание частиц пыли"""

        # вычисление координат, в какую сторону вылетать частицам
        x = self.rect.bottomright[0] - 9 if self.direction == 'left' \
            else self.rect.bottomleft[0] + 9
        y = self.rect.bottomleft[1] + 2
        Particles(self.direction, (x, y))

    def rest_of_boost(self, name) -> str:
        """Остаток времени действия зелья"""

        if not self.boosts[name]['last_boost']:
            return '0'
        return str(ceil((self.boosts[name]['boost_duration'] -
                         (pygame.time.get_ticks() - self.boosts[name][
                             'last_boost'])) / 1000))

    def set_speed(self, speedup):
        """Установка новой скорости ГГ"""

        self.speed = self.last_speed + speedup

    def set_damage(self, delta_damage):
        """Установка нового урона ГГ"""

        self.damage = self.last_damage + delta_damage

    def add_paused_time(self, time):
        """Добавление к каждому бусту время паузы"""

        for name in self.boosts:
            self.boosts[name]['last_boost'] += time
