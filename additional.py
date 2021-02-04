import os
import pygame

pygame.init()
size = width, height = 700, 700
tile_width = tile_height = 80  # размеры клетки
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Game...')
clock = pygame.time.Clock()
fps = 10


def load_image(name, colorkey=None):
    """Загрузка изображения"""
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        raise SystemExit(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    """Загрузка уровня"""
    filename = os.path.join('data', filename)
    if not os.path.isfile(filename):
        raise SystemExit(f"Файл с картой '{filename}' не найден")
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(load_image('grass.png'),
                                            (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, image, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        # список фреймов для различных отрисовок спрайта
        self.frames = []
        self.height_jump = tile_height * 2
        self.speed = 0
        self.life = True
        self.vector = 'right'
        self.attack_ = False
        self.jump = False
        self.cut_image(image, columns, rows)
        # изначально спрайт получает самый первый фрейм
        self.frame_number = 0
        self.image = self.frames[self.frame_number]
        self.rect = self.rect.move(x, y)

    def cut_image(self, image, columns, rows):
        self.rect = pygame.Rect(0, 0, image.get_width() // columns,
                                image.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(image.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if not self.life:
            if self.frame_number != 17:
                self.frame_number += 1
            else:
                return
        if self.attack_:
            self.frame_number += 1
            if self.frame_number == 13:
                self.attack_ = False
                self.frame_number = 0
        while self.rect.bottom < height and \
                not pygame.sprite.spritecollideany(self, tiles_group) \
                and not self.jump:
            self.rect.y += 1

        if self.jump:
            self.jump -= 5
            self.rect.y += 5

        if pygame.key.get_pressed()[pygame.K_RIGHT] or \
                pygame.key.get_pressed()[pygame.K_LEFT]:
            self.frame_number = (self.frame_number + 1) % (
                        len(self.frames) * 1 // 3)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            for sprite in tiles_group:
                sprite.rect.x -= tile_width
            if pygame.sprite.spritecollideany(self, tiles_group):
                for sprite in tiles_group:
                    sprite.rect.x += tile_width
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            for sprite in tiles_group:
                sprite.rect.x += tile_width
            if pygame.sprite.spritecollideany(self, tiles_group):
                for sprite in tiles_group:
                    sprite.rect.x -= tile_width
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            self.rect.y += self.jump
            self.jump = False
        elif pygame.key.get_pressed()[pygame.K_UP]:
            if not self.jump:
                self.jump = self.height_jump
                self.speed = 1
                self.rect.y -= self.height_jump
        self.image = self.frames[self.frame_number]
        if self.vector == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))

    def attack(self):
        if self.life:
            self.attack_ = True
            self.frame_number = 6

    def smert(self):
        if self.life:
            self.life = False
            self.frame_number = 13


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in '#.':
                Tile(x, y)
            elif level[y][x] == '@':
                Tile(x, y)
                new_player = AnimatedSprite(load_image("123.jpg", -1),
                                            6, 3, x * tile_width, y * tile_height)
    if new_player is None:
        raise SystemExit("На карте нет игрока")
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    """Выход"""
    pygame.quit()
    sys.exit()


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bg = pygame.transform.scale(load_image('bg.jpg'), (width, height))

screen.blit(bg, (0, 0))
x, y = 0, height - tile_height
player = AnimatedSprite(load_image("123.jpg", -1), 6, 3, x, y)
# level = Level_02(player)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.attack()
            if event.key == pygame.K_f:
                player.smert()
            if event.key == pygame.K_LEFT:
                player.vector = 'left'
            if event.key == pygame.K_RIGHT:
                player.vector = 'right'

    # screen.fill(pygame.Color("white"))
    screen.blit(bg, (0, 0))

    player_group.draw(screen)

    all_sprites.update()
    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
