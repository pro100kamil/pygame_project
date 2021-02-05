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
    new_player, x, y = None, None, None
    for y, row in enumerate(level_map):
        for x, elem in enumerate(row):
            if elem == '-':
                Platform(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '@':
                new_player = NinjaFrog(x * TILE_SIDE - 18,
                                       y * TILE_SIDE + 18, 5)

    return new_player, x, y


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


class NinjaFrog(BaseHero):
    width, height = 32, 32

    hit_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Hit (32x32).png'), 1, 7, anim_delay=100))
    jump_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Jump (32x32).png'), 1, 1, anim_delay=100))
    fall_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Fall (32x32).png'), 1, 1, anim_delay=100))
    run_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Run (32x32).png'), 1, 12, anim_delay=100))
    stay_anim = pyganim.PygAnimation(cut_image(
        load_image('Ninja Frog/Idle (32x32).png'), 1, 11, anim_delay=100))

    run_anim.play()
    stay_anim.play()
    jump_anim.play()
    fall_anim.play()
    hit_anim.play()

    def __init__(self, x, y, speed):
        super().__init__(x, y, NinjaFrog.width, NinjaFrog.height)
        self.direction = "right"
        self.speed = speed
        self.jump, self.x_vel, self.y_vel = 0, 0, 0
        self.height_jump = 10

    def flip(self):
        """Разворот всех анимаций спрайтов"""
        NinjaFrog.stay_anim.flip(True, False)
        NinjaFrog.run_anim.flip(True, False)
        NinjaFrog.jump_anim.flip(True, False)
        NinjaFrog.fall_anim.flip(True, False)
        NinjaFrog.hit_anim.flip(True, False)

    def collide(self):
        self.rect.x += self.x_vel
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.x_vel < 0:
                self.rect.left = platform.rect.right
                self.x_vel = 0
            elif self.x_vel > 0:
                self.rect.right = platform.rect.left
                self.x_vel = 0
        self.x_vel = 0

        self.rect.y += self.y_vel
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.y_vel > 0:
                self.on_ground = True
                self.jump = False
                self.rect.bottom = platform.rect.top
            elif self.y_vel < 0:
                self.rect.top = platform.rect.bottom
            self.y_vel = 0

    def update(self):
        super().update()

        # флаг, нужна ли ещё анимация в текущем обновлении
        flag_anim = True  # нужно, чтобы не было двойной анимации

        if not self.on_ground:
            self.y_vel += GRAVITY
        else:
            self.y_vel = 1
            self.on_ground = False

        self.collide()

        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_vel = self.speed

            if self.direction == "left":
                self.direction = "right"
                self.flip()
            NinjaFrog.run_anim.blit(self.image, (0, 0))
            flag_anim = False
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x_vel = -self.speed

            if self.direction == "right":
                self.direction = "left"
                self.flip()
            if flag_anim:
                NinjaFrog.run_anim.blit(self.image, (0, 0))
                flag_anim = False
        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.on_ground:
                self.on_ground = False
                self.y_vel = -self.height_jump
            if flag_anim:
                NinjaFrog.jump_anim.blit(self.image, (0, 0))
                flag_anim = False
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.y_vel = 2 * self.height_jump
            if flag_anim:
                NinjaFrog.fall_anim.blit(self.image, (0, 0))
                flag_anim = False
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            if flag_anim:
                NinjaFrog.hit_anim.blit(self.image, (0, 0))
                flag_anim = False
        # if not any(pygame.key.get_pressed()):  # все клавиши не нажаты
        if flag_anim:
            NinjaFrog.stay_anim.blit(self.image, (0, 0))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(platforms, all_sprites)

        picture = load_image('grass.png')
        self.image = pygame.transform.scale(picture, (TILE_SIDE, TILE_SIDE))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


if __name__ == "__main__":
    running = True
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    player, level_x, level_y = load_level('map.txt')

    camera = Camera((level_x, level_y))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        screen.fill(pygame.Color("light blue"))
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
