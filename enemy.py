import pygame
import os
import pyganim


TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750
FPS = 30
GRAVITY = 10 / FPS

pygame.init()
screen = pygame.display.set_mode(SIZE)


def cut_sheet(filename, rows, cols, anim_delay):

    sheet: pygame.Surface = load_image(filename)
    picture_w, picture_h = sheet.get_width() // cols, sheet.get_height() // rows
    frames = []
    for y in range(rows):
        for x in range(cols):
            frame_location = (picture_w * x, picture_h * y)
            frames.append((sheet.subsurface(frame_location, (picture_w, picture_h)), anim_delay))

    return frames


def load_image(name, color_key=None):
    """Загрузка изображения"""
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        raise SystemExit(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    """Загрузка уровня"""
    filename = os.path.join('data', filename)

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for y, row in enumerate(level_map):
        for x, elem in enumerate(row):
            if elem == '-':
                Platform(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '*':
                BouncedEnemy(x * TILE_SIDE, y * TILE_SIDE, 10)
            elif elem == '@':
                WalkingEnemy(x * TILE_SIDE, y * TILE_SIDE, 2, 100)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__(all_sprites)

        self.width, self.height = width, height

        self.start_x, self.start_y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height))
        self.x_vel, self.y_vel = None, None
        self.on_ground = False

    def update(self):
        self.rect = self.rect.move(self.x_vel, self.y_vel)

        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_position(self):
        return self.rect.x, self.rect.y


class BouncedEnemy(Enemy):
    width, height = 34, 44

    jump_anim = pyganim.PygAnimation(cut_sheet('Bunny/Jump.png', 1, 1, anim_delay=100))
    stay_anim = pyganim.PygAnimation(cut_sheet('Bunny/Idle.png', 1, 8, anim_delay=100))
    fall_anim = pyganim.PygAnimation(cut_sheet('Bunny/Fall.png', 1, 1, anim_delay=100))
    jump_anim.play()
    stay_anim.play()
    fall_anim.play()

    def __init__(self, x, y, jump):
        super().__init__(x, y, BouncedEnemy.width, BouncedEnemy.height)
        self.jump, self.x_vel, self.y_vel = jump, 0, 0
        self.last_fall = pygame.time.get_ticks()
        self.just_fell = True

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

        self.collide()

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
            BouncedEnemy.stay_anim.blit(self.image, (0, 0))

        if not self.on_ground:
            self.y_vel += GRAVITY
            if self.y_vel > 0:
                BouncedEnemy.fall_anim.blit(self.image, (0, 0))
            else:
                BouncedEnemy.jump_anim.blit(self.image, (0, 0))


class WalkingEnemy(Enemy):
    width, height = 32, 34

    left_anim = pyganim.PygAnimation(cut_sheet('Chicken/Run.png', 1, 14, anim_delay=100))
    right_anim = pyganim.PygAnimation(cut_sheet('Chicken/RunReverse.png', 1, 14, anim_delay=100))
    stay_anim = pyganim.PygAnimation(cut_sheet('Chicken/Idle.png', 1, 13, anim_delay=100))
    left_anim.play()
    right_anim.play()
    stay_anim.play()

    def __init__(self, x, y, speed, max_length):
        super().__init__(x, y, WalkingEnemy.width, WalkingEnemy.height)
        self.x_vel, self.y_vel = speed, 0
        self.max_length = max_length

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
                self.x_vel = -self.x_vel

            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
                self.x_vel = -self.x_vel

    def update(self):
        super().update()

        self.collide()

        if abs(self.rect.x - self.start_x) >= self.max_length:
            self.x_vel = -self.x_vel

        if self.x_vel > 0:
            WalkingEnemy.right_anim.blit(self.image, (0, 0))
        elif self.x_vel < 0:
            WalkingEnemy.left_anim.blit(self.image, (0, 0))
        else:
            WalkingEnemy.stay_anim.blit(self.image, (0, 0))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(platforms, all_sprites)

        picture = load_image('grass.png')
        self.image = pygame.transform.scale(picture, (TILE_SIDE, TILE_SIDE))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


running = True
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
load_level('map.txt')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(pygame.Color("light blue"))
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()