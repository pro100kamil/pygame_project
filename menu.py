import pygame
import pygame_gui
from collections import namedtuple

if __name__ == '__main__':
    hero_parameters = namedtuple('hero_parameters', 'damage speed health')
    # name: (damage, speed, health)
    heroes = {'Ninja Frog': hero_parameters(15, 6, 100),
              'Pink Man': hero_parameters(20, 4, 120),
              'Virtual Guy': hero_parameters(15, 7, 95),
              'Mask Dude': hero_parameters(15, 6, 100)}
    list_heroes = list(heroes.keys())
    now = 0
    pygame.init()
    pygame.display.set_caption('Menu')
    SIZE = WIDTH, HEIGHT = 750, 750
    screen = pygame.display.set_mode(SIZE)

    # координаты и размер изображения гг
    size_hero_image = 300, 300
    coord_hero_image = (WIDTH - size_hero_image[0]) // 2, 50
    image = pygame.transform.scale(pygame.image.load("Ninja Frog.png"),
                                   size_hero_image)

    manager = pygame_gui.UIManager(SIZE)

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

    clock = pygame.time.Clock()

    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # exit(0)
                confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                    rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 100),
                                     (300, 200)),
                    manager=manager,
                    window_title='Подтверждение',
                    action_long_desc='Вы уверены, что хотите выйти?',
                    action_short_name='OK',
                    blocking=True
                )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    now = (now + 1) % len(list_heroes)
                elif event.key == pygame.K_LEFT:
                    now = (now - 1) % len(list_heroes)
                image = pygame.transform.scale(
                    pygame.image.load(f"{list_heroes[now]}.png"),
                    size_hero_image)
                damage_label.set_text(
                    f'Урон: {heroes[list_heroes[now]].damage}')
                speed_label.set_text(
                    f'Скорость: {heroes[list_heroes[now]].speed}')
                health_label.set_text(
                    f'Жизни: {heroes[list_heroes[now]].health}')
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    running = False
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    image = pygame.transform.scale(
                        pygame.image.load(f"{event.text}.png"),
                        size_hero_image)
                    damage_label.set_text(f'Урон: {heroes[event.text].damage}')
                    speed_label.set_text(
                        f'Скорость: {heroes[event.text].speed}')
                    health_label.set_text(
                        f'Жизни: {heroes[event.text].health}')
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play:
                        print('PLAY')
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        screen.fill(pygame.Color('light blue'), (*coord_hero_image,
                                                 *size_hero_image))

        screen.blit(image, (*coord_hero_image,
                            *size_hero_image))

        manager.draw_ui(screen)
        pygame.display.update()
    pygame.quit()
