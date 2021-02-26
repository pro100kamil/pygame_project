import pyganim

from functions import *


class Shuriken(pygame.sprite.Sprite):
    """Сюрикен"""
    width, height = 25, 25

    def __init__(self, x, y, direction, range_flight=200):
        super().__init__(all_sprites)

        self.rect = pygame.Rect(x, y, Shuriken.width, Shuriken.height)
        self.image = pygame.Surface((Shuriken.width, Shuriken.height))

        self.image.fill('black')
        self.image.set_colorkey('black')

        self.move_anim = pyganim.PygAnimation(
            cut_sheet('move_shuriken.png', 1, 13, anim_delay=100))
        self.move_anim.play()

        self.direction = direction
        if self.direction == "right":
            self.move_anim.flip(True, False)
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
        self.move_anim.blit(self.image, (0, 0))

    def update(self):
        for enemy in pygame.sprite.spritecollide(self, enemies_group, False):
            enemy.get_hit(self.damage)

            sound_manager.play_hit()
            self.kill()
        if self.flown + self.delta <= self.range_flight and \
                not pygame.sprite.spritecollideany(self, platforms) and \
                not pygame.sprite.spritecollideany(self, spikes_group):
            self.move()
        else:  # полёт закончен
            self.flown = 0
            self.kill()


class Bullet(pygame.sprite.Sprite):
    """Пуля растения"""
    width, height = 22, 22

    def __init__(self, x, y, direction, range_flight=300):
        super().__init__(all_sprites, bullets_group)

        self.rect = pygame.Rect(x, y, Bullet.width, Bullet.height)
        self.image = pygame.Surface((Bullet.width, Bullet.height))

        self.move_anim = pyganim.PygAnimation(
            cut_image(pygame.transform.scale(
                load_image('Enemies/Plant/Bullet.png'), (Bullet.width, Bullet.height)),
                1, 1, anim_delay=100))
        self.move_anim.play()

        self.image.fill('black')
        self.image.set_colorkey('black')

        self.direction = direction

        self.range_flight = range_flight  # дальность полёта
        self.delta = self.range_flight / 26
        self.flown = 0  # сколько пуля уже пролетела
        # урон, который получит персонаж, если в него попадёт пуля
        self.damage = 10

    def get_damage(self):
        return self.damage

    def get_direction(self):
        return self.direction

    def move(self):
        if self.direction == "right":
            self.rect.x += self.delta
        else:
            self.rect.x -= self.delta
        self.flown += self.delta
        self.move_anim.blit(self.image, (0, 0))

    def update(self):
        if self.flown + self.delta <= self.range_flight and \
                not pygame.sprite.spritecollideany(self, platforms) and \
                not pygame.sprite.spritecollideany(self, spikes_group):
            self.move()
        else:  # полёт закончен
            self.flown = 0
            self.kill()
