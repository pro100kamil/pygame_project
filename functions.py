import os

from constants import *


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


def cut_image(sheet, rows, cols, anim_delay):
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


def draw_top_bar():
    """Отображение верхней панели"""
    font = pygame.font.Font(None, 30)
    if not list(player_group):
        text = font.render("Вы проиграли", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2,
                           TILE_SIDE // 2 - 10))
        return
    player = list(player_group)[0]
    first = (WIDTH - (50 * 4 + 50 * 4 + 250)) // 2
    screen.blit(pygame.transform.scale(load_image('Heart2.png'), (40, 40)),
                (first, TILE_SIDE // 2 - 20))
    screen.blit(font.render(f": {player.get_health()}",
                            True, (0, 252, 123)),
                (first + 50, TILE_SIDE // 2 - 10))
    screen.blit(pygame.transform.scale(load_image('stay_shuriken.png', -1),
                                       (36, 36)),
                (first + 110, TILE_SIDE // 2 - 18))
    screen.blit(font.render(f": {player.get_number_shurikens()}",
                            True, (0, 252, 123)),
                (first + 160, TILE_SIDE // 2 - 10))

    screen.blit(pygame.transform.scale(load_image('potion_speed.png', -1),
                                       (20, 30)),
                (first + 220, TILE_SIDE // 2 - 15))

    screen.blit(
        font.render(player.rest_of_boost('speed') + ' с', True, (0, 252, 123)),
        (first + 270, TILE_SIDE // 2 - 10))

    screen.blit(pygame.transform.scale(load_image('potion_damage.png', -1),
                                       (20, 30)),
                (first + 330, TILE_SIDE // 2 - 15))

    screen.blit(font.render(player.rest_of_boost('damage') + ' с', True,
                            (0, 252, 123)),
                (first + 380, TILE_SIDE // 2 - 10))

    screen.blit(font.render(f"Врагов осталось: "
                            f"{len(list(enemies_group))}",
                            True, (0, 252, 123)),
                (first + 440, TILE_SIDE // 2 - 10))
