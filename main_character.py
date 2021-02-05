import pygame
import os
import pyganim

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 1050, 750
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
            frames.append((sheet.subsurface(frame_location,
                                            (picture_w, picture_h)),
                           anim_delay))

    return frames


def cut_image(sheet: pygame.Surface, rows, cols, anim_delay):
    picture_w, picture_h = sheet.get_width() // cols, sheet.get_height() // rows
    frames = []
    for y in range(rows):
        for x in range(cols):
            frame_location = (picture_w * x, picture_h * y)
            frames.append((sheet.subsurface(frame_location,
                                            (picture_w, picture_h)),
                           anim_delay))

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
    # если файл не существует, то выходим
    if not os.path.isfile(filename):
        raise SystemExit(f"Файл с картой '{filename}' не найден")

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    for y, row in enumerate(level_map):
        for x, elem in enumerate(row):
            if elem == '-':
                Platform(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '@':
                NinjaFrog(x * TILE_SIDE - 18, y * TILE_SIDE + 18, 5)


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
        self.rect = self.rect.move(self.x_vel, self.y_vel)

        self.image.fill('black')
        self.image.set_colorkey('black')

    def get_position(self):
        return self.rect.x, self.rect.y


class NinjaFrog(BaseHero):
    width, height = 32, 32

    hit_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Hit (32x32).png'), 1, 7, anim_delay=100))
    jump_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Jump (32x32).png'), 1, 1, anim_delay=100))
    fall_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Fall (32x32).png'), 1, 1, anim_delay=100))
    left_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Run (32x32).png'), 1, 12, anim_delay=100))
    right_anim = pyganim.PygAnimation(cut_image(
        pygame.transform.flip(load_image('Ninja Frog/Run (32x32).png'),
                              True, False), 1, 12, anim_delay=100))
    stay_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Idle (32x32).png'), 1, 11, anim_delay=100))
    left_anim.play()
    right_anim.play()
    stay_anim.play()
    jump_anim.play()
    fall_anim.play()
    hit_anim.play()

    def __init__(self, x, y, speed):
        super().__init__(x, y, NinjaFrog.width, NinjaFrog.height)
        self.direction = "right"
        self.speed = speed
        self.jump, self.x_vel, self.y_vel = 0, 0, 0

    def collide(self):
        lst = pygame.sprite.spritecollide(self, platforms, False)
        for platform in lst:
            if self.y_vel > 0:
                self.on_ground = True
                self.jump = False
                self.rect.bottom = platform.rect.top
                self.y_vel = 0
            elif self.y_vel < 0:
                self.rect.top = platform.rect.bottom
                self.y_vel = 0
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
                self.x_vel = 0
            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
                self.x_vel = 0
        if self.x_vel:
            self.x_vel = 0

    def update(self):
        super().update()

        self.collide()

        if self.on_ground:
            if self.jump:
                self.y_vel = -self.jump
                self.on_ground = False
            NinjaFrog.stay_anim.blit(self.image, (0, 0))

        if not self.on_ground:
            self.y_vel += GRAVITY
            if self.y_vel > 0:
                NinjaFrog.fall_anim.blit(self.image, (0, 0))
            else:
                NinjaFrog.jump_anim.blit(self.image, (0, 0))

        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_vel = self.speed

            if self.direction == "left":
                self.direction = "right"
                NinjaFrog.stay_anim.flip(True, False)
            NinjaFrog.left_anim.blit(self.image, (0, 0))
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x_vel = -self.speed

            if self.direction == "right":
                self.direction = "left"
                NinjaFrog.stay_anim.flip(True, False)
            NinjaFrog.right_anim.blit(self.image, (0, 0))
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            self.jump = 0

            NinjaFrog.fall_anim.blit(self.image, (0, 0))
        elif pygame.key.get_pressed()[pygame.K_UP]:
            self.jump = 10

            NinjaFrog.jump_anim.blit(self.image, (0, 0))
        elif pygame.key.get_pressed()[pygame.K_RETURN]:
            NinjaFrog.hit_anim.blit(self.image, (0, 0))
        else:
            NinjaFrog.stay_anim.blit(self.image, (0, 0))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(platforms, all_sprites)

        picture = load_image('grass.png')
        self.image = pygame.transform.scale(picture, (TILE_SIDE, TILE_SIDE))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


if __name__ == "__main__":
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
