import os
import pygame
import pyganim

TILE_SIDE = 50
SIZE = WIDTH, HEIGHT = 750, 750
FPS = 30
GRAVITY = 10 / FPS

pygame.init()
screen = pygame.display.set_mode(SIZE)


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


class Shuricken(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        super().__init__(all_sprites)

        self.image = pygame.transform.scale(load_image('shuriken.png'),
                                            (TILE_SIDE // 2, TILE_SIDE // 2))

        self.width, self.height = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.direction = "right"
        self.delta = 20
        self.range_flight = 100  # дальность полёта
        self.flown = 0  # уже пролетел
        # урон, который получит персонаж, если в него попадёт сюрикен
        self.damage = 30

    def move(self):
        if self.direction == "right":
            self.rect.x += self.delta
        else:
            self.rect.x -= self.delta
        self.flown += self.delta

    def update(self):
        if self.flown:
            if self.flown < self.range_flight:
                self.move()
            else:  # полёт закончен
                self.flown = 0
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.move()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.direction = "left"
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.direction = "right"


if __name__ == "__main__":
    running = True
    clock = pygame.time.Clock()

    # группы спрайтов
    all_sprites = pygame.sprite.Group()

    Shuricken(100, 200)

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
