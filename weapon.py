import os
import pygame
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


class Shuriken(pygame.sprite.Sprite):

    width, height = 25, 25

    move_anim = pyganim.PygAnimation(
        cut_sheet('move_shuriken.png', 1, 13, anim_delay=100))
    move_anim.flip(True, False)
    stay_anim = pyganim.PygAnimation(
        cut_sheet('stay_shuriken.png', 1, 1, anim_delay=100))
    move_anim.play()
    stay_anim.play()

    def __init__(self, x, y,):
        super().__init__(all_sprites)

        self.rect = pygame.Rect(x, y, Shuriken.width, Shuriken.height)
        self.image = pygame.Surface((Shuriken.width, Shuriken.height))

        self.direction = "right"
        self.range_flight = 100  # дальность полёта
        self.delta = self.range_flight / 26
        self.flown = 0  # сколько сюрикен уже пролетел
        # урон, который получит персонаж, если в него попадёт сюрикен
        self.damage = 30

    def move(self):
        if self.direction == "right":
            self.rect.x += self.delta
        else:
            self.rect.x -= self.delta
        self.flown += self.delta
        Shuriken.move_anim.blit(self.image, (0, 0))

    def update(self):
        self.image.fill('black')
        self.image.set_colorkey('black')

        if self.flown:
            if self.flown < self.range_flight:
                self.move()
            else:  # полёт закончен
                self.flown = 0
        else:
            self.stay_anim.blit(self.image, (0, 0))
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.move()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            if self.direction == "right":
                self.direction = "left"
                Shuriken.move_anim.flip(True, False)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            if self.direction == "left":
                self.direction = "right"
                Shuriken.move_anim.flip(True, False)


if __name__ == "__main__":
    running = True
    clock = pygame.time.Clock()

    # группы спрайтов
    all_sprites = pygame.sprite.Group()

    Shuriken(100, 200)

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
