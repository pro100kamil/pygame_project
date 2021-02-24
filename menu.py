import pygame
import pygame_gui
from collections import namedtuple

pygame.init()
SIZE = WIDTH, HEIGHT = 750, 750
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
FPS = 30
sound = True  # вначале звук включён


def terminate():
    """Немедленный выход"""
    pygame.quit()
    exit(0)


def exit_warning(manager):
    """Открывает окно с предупреждением о выходе"""
    pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 100),
                         (300, 200)),
        manager=manager,
        window_title='Подтверждение',
        action_long_desc='Вы уверены, что хотите выйти?',
        action_short_name='OK',
        blocking=True
    )


def menu_screen():
    """Открывает окно меню"""
    global sound
    pygame.display.set_caption('Menu')
    hero_parameters = namedtuple('hero_parameters', 'damage speed health')
    # name: (damage, speed, health)
    heroes = {'Ninja Frog': hero_parameters(15, 6, 100),
              'Pink Man': hero_parameters(20, 4, 120),
              'Virtual Guy': hero_parameters(15, 7, 95),
              'Mask Dude': hero_parameters(15, 6, 100)}
    list_heroes = list(heroes.keys())
    now = 0
    # координаты и размер изображения гг
    size_hero_image = 300, 300
    coord_hero_image = (WIDTH - size_hero_image[0]) // 2, 50
    image = pygame.transform.scale(pygame.image.load("Ninja Frog.png"),
                                   size_hero_image)

    manager = pygame_gui.UIManager(SIZE, 'style.json')

    width = 31
    height = 33
    x = coord_hero_image[0] + (size_hero_image[0] - width) // 2
    y = 10
    volume = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text='',
        tool_tip_text='Нажмите, чтобы выключить звук',
        object_id='#volume',
        manager=manager
    )

    width = 180
    height = 50
    x = coord_hero_image[0] + (size_hero_image[0] - width) // 2
    y = coord_hero_image[1] + size_hero_image[1] + 20
    name_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y, width, height),
        text='Ninja Frog',
        manager=manager
    )
    damage_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + height, width, height),
        text=f'Урон: {heroes["Ninja Frog"].damage}',
        manager=manager
    )
    speed_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + 2 * height, width, height),
        text=f'Скорость: {heroes["Ninja Frog"].speed}',
        manager=manager
    )
    health_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + 3 * height, width, height),
        text=f'Жизни: {heroes["Ninja Frog"].health}',
        manager=manager
    )

    width_play = 200
    height_play = 80
    play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WIDTH // 3 + (WIDTH // 3 - width_play) // 2,
                                  y + 4 * height + 40, width_play,
                                  height_play),
        text='PLAY',
        tool_tip_text='Нажмите, чтобы начать игру',
        manager=manager
    )

    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_warning(manager)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    now = (now + 1) % len(list_heroes)
                elif event.key == pygame.K_LEFT:
                    now = (now - 1) % len(list_heroes)
                name = list_heroes[now]
                image = pygame.transform.scale(
                    pygame.image.load(f"{name}.png"),
                    size_hero_image)
                damage_label.set_text(
                    f'Урон: {heroes[name].damage}')
                speed_label.set_text(
                    f'Скорость: {heroes[name].speed}')
                health_label.set_text(
                    f'Жизни: {heroes[name].health}')
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    terminate()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play:
                        print('PLAY')
                        level_selection_screen()
                    elif event.ui_element == volume:
                        sound = not sound
                        print('Звук включён' if sound else 'Звук выключен')
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        screen.fill(pygame.Color('light blue'), (*coord_hero_image,
                                                 *size_hero_image))

        screen.blit(image, (*coord_hero_image,
                            *size_hero_image))

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def level_selection_screen():
    """Открывает окно выбора уровня"""
    pygame.display.set_caption('Level selection')
    kol_levels = 10
    images = []
    size = 80, 80
    for i in range(1, kol_levels + 1):
        images.append(pygame.transform.scale(
            pygame.image.load(f"Levels/{str(i).rjust(2, '0')}.png"), size))

    rects = []  # прямоугольники, в которых лежат изображения
    delta = 50
    y = (HEIGHT - size[1] * 2 - delta) // 2
    x0 = (WIDTH - size[0] * kol_levels // 2) // 2
    for i in range(kol_levels // 2):
        x = x0 + size[0] * i
        rects.append(pygame.Rect(x, y, *size))
    y += size[1] + delta
    for i in range(kol_levels // 2, kol_levels):
        x = x0 + size[0] * (i - kol_levels // 2)
        rects.append(pygame.Rect(x, y, *size))

    manager = pygame_gui.UIManager(SIZE, 'style.json')

    width = 31
    height = 33
    x = 10
    y = 10
    back = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text='',
        tool_tip_text='Нажмите, вернуться назад',
        object_id='#back',
        manager=manager
    )

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_warning(manager)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(rects, start=1):
                        if pygame.Rect.collidepoint(rect, event.pos):
                            print(i)
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    terminate()
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == back:
                        pygame.display.set_caption('Menu')
                        running = False
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        font = pygame.font.Font(None, 50)
        text = font.render("Выберите уровень", True, (0, 0, 0))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = 150
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                             text_w + 20, text_h + 20), 2)

        for i in range(len(images)):
            screen.blit(images[i], rects[i])

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    menu_screen()
