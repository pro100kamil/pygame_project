from collections import namedtuple

import pygame_gui

from enemy import *
from main_character import MainHero
from some_classes import *


def terminate():
    """Немедленный выход"""
    pygame.quit()
    exit(0)


def exit_warning(manager, msg='Вы уверены, что хотите выйти?'):
    """Открывает окно с предупреждением о выходе"""
    pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 100),
                         (300, 200)),
        manager=manager,
        window_title='Подтверждение',
        action_long_desc=msg,
        action_short_name='OK',
        blocking=False
    )


def menu_screen():
    """Открывает окно меню и возращает имя героя и номер выбранного уровня"""
    global MAIN_HERO

    sound_manager.play_menu_music()

    pygame.display.set_icon(load_image('for menu/Ninja Frog.png'))
    sound = True  # вначале звук включён
    pygame.display.set_caption('Меню')
    hero_parameters = namedtuple('hero_parameters', 'damage speed health')
    # name: (damage, speed, health)
    heroes = {'Ninja Frog': hero_parameters(15, 6, 100),
              'Pink Man': hero_parameters(20, 4, 120),
              'Virtual Guy': hero_parameters(15, 7, 95),
              'Mask Dude': hero_parameters(15, 6, 100)}
    list_heroes = list(heroes.keys())
    now = 0
    MAIN_HERO = list_heroes[now]
    # координаты и размер изображения главного героя
    size_hero_image = 300, 300
    coord_hero_image = (WIDTH - size_hero_image[0]) // 2, 50
    image = pygame.transform.scale(load_image("for menu/Ninja Frog.png"),
                                   size_hero_image)
    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')
    width = 31
    height = 33
    x = coord_hero_image[0] + (size_hero_image[0] - width) // 2
    y = 10
    volume = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text='',
        tool_tip_text='Нажмите, чтобы включить/выключить звук',
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
        time_delta = 1000 / FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_warning(manager)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    now = (now + 1) % len(list_heroes)
                elif event.key == pygame.K_LEFT:
                    now = (now - 1) % len(list_heroes)
                elif event.key == pygame.K_RETURN:
                    print('PLAY')
                    level_selection_screen()
                    continue
                elif event.key == pygame.K_ESCAPE:
                    exit_warning(manager)
                name = list_heroes[now]
                image = pygame.transform.scale(
                    load_image(f"for menu/{name}.png"), size_hero_image)
                name_label.set_text(name)
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
                        if sound:
                            print('Звук включён')
                            sound_manager.start_sound()
                        else:
                            print('Звук выключен')
                            sound_manager.remove_sound()
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        screen.blit(image, (*coord_hero_image,
                            *size_hero_image))

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def level_selection_screen():
    """Открывает окно выбора уровня и возращает номер выбранного уровня"""
    global NOW_LEVEL
    pygame.display.set_caption('Выберите уровень')
    kol_levels = 10
    images = []
    size = 80, 80
    for i in range(1, kol_levels + 1):
        images.append(pygame.transform.scale(
            load_image(f"for menu/Levels/{str(i).rjust(2, '0')}.png"), size))
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

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')

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
        time_delta = 1000 / FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_caption('Меню')
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(rects, start=1):
                        if pygame.Rect.collidepoint(rect, event.pos):
                            if os.path.isfile(f'maps/level{i}.txt'):
                                NOW_LEVEL = i
                                game()
                                return
                            else:
                                # окно с предупреждением
                                pygame_gui.windows.UIMessageWindow(
                                    rect=pygame.Rect(
                                        WIDTH // 2 - 150, HEIGHT // 2 + 150,
                                        300, 300),
                                    html_message='Такого уровня пока нет',
                                    manager=manager
                                )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_caption('Меню')
                    running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == back:
                        pygame.display.set_caption('Меню')
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


def level_complete_screen(win=True):
    """Открывает окно после прохождения/проигрыша уровня"""
    global NOW_LEVEL

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')

    width = 31
    height = 33
    x = 10
    y = 10
    delta = 40
    back = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text='',
        tool_tip_text='Нажмите, вернуться назад',
        object_id='#back',
        manager=manager
    )
    levels = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x + delta, y, width, height),
        text='',
        tool_tip_text='Нажмите, чтобы перейти к выбору уровня',
        object_id='#levels',
        manager=manager
    )
    restart = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x + 2 * delta, y, width, height),
        text='',
        tool_tip_text='Нажмите, чтобы пройти этот уровень ещё раз',
        object_id='#restart',
        manager=manager
    )
    if win:
        next_level = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x + 3 * delta, y, width, height),
            text='',
            tool_tip_text='Нажмите, чтобы перейти к следующему уровню',
            object_id='#next',
            manager=manager
        )
    else:
        next_level = None

    running = True
    while running:
        time_delta = 1000 / FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_caption('Меню')
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_caption('Меню')
                    running = False
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == back:
                        pygame.display.set_caption('Меню')
                        sound_manager.play_menu_music()
                    elif event.ui_element == levels:
                        sound_manager.play_menu_music()
                        level_selection_screen()
                    elif event.ui_element == restart:
                        game()
                    elif event.ui_element == next_level:
                        NOW_LEVEL += 1
                        game()
                    running = False
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        font = pygame.font.Font(None, 50)
        text = font.render("Уровень пройден!" if win else "Вы проиграли",
                           True, (0, 0, 0))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = 150
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        pygame.draw.rect(screen, (0, 0, 0), (text_x - 10, text_y - 10,
                                             text_w + 20, text_h + 20), 2)

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename, MAIN_HERO):
    """Загрузка уровня"""
    filename = os.path.join('maps', filename)
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
            elif elem == '1':
                Checkpoint(
                    x * TILE_SIDE - (TILE_SIDE - Checkpoint.width),
                    y * TILE_SIDE + (TILE_SIDE - Checkpoint.height),
                    'Start')
            elif elem == '9':
                Checkpoint(
                    x * TILE_SIDE - (TILE_SIDE - Checkpoint.width),
                    y * TILE_SIDE + (TILE_SIDE - Checkpoint.height),
                    'End')
            elif elem == '`':
                Saw(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '.':
                Spikes(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'c':
                Chicken(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'o':
                AngryPig(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == '*':
                Fruit(x * TILE_SIDE + (TILE_SIDE - Fruit.width) / 2,
                      y * TILE_SIDE + (TILE_SIDE - Fruit.height) / 2)
            elif elem == '?':
                Potion(x * TILE_SIDE + (TILE_SIDE - Potion.width) / 2,
                       y * TILE_SIDE + (TILE_SIDE - Potion.height) / 2)
            elif elem == '2':
                Backpack(x * TILE_SIDE + (TILE_SIDE - Backpack.width) / 2,
                         y * TILE_SIDE + (TILE_SIDE - Backpack.height) / 2)
            elif elem == 'b':
                Bunny(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'm':
                Mushroom(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 's':
                Slime(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'h':
                Chameleon(x * TILE_SIDE, y * TILE_SIDE)
            elif elem == 'r':
                Rino(
                    x * TILE_SIDE - (TILE_SIDE - Rino.width),
                    y * TILE_SIDE + (TILE_SIDE - Rino.height)
                )
            elif elem == 'p':
                Plant(
                    x * TILE_SIDE - (TILE_SIDE - Plant.width) + 20,
                    y * TILE_SIDE + (TILE_SIDE - Plant.height), "right"
                )
            elif elem == 'P':
                Plant(
                    x * TILE_SIDE - (TILE_SIDE - Plant.width) + 20,
                    y * TILE_SIDE + (TILE_SIDE - Plant.height), "left"
                )
            elif elem == '@':
                new_player = MainHero(
                    x * TILE_SIDE - (TILE_SIDE - MainHero.width),
                    y * TILE_SIDE + (TILE_SIDE - MainHero.height), MAIN_HERO)

    return new_player, (x + 1) * TILE_SIDE, (y + 1) * TILE_SIDE


def game():
    with open('log.txt') as file:
        # уровень, на котором остановился игрок (этот уровень ещё не пройден)
        max_level = int(file.read())
    if NOW_LEVEL > max_level:
        level_selection_screen()
        return

    sound_manager.play_game_music()

    pygame.display.set_caption('Игра')

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')

    running = True
    pause = False
    last_pause = 0

    player, level_x, level_y = load_level(f'level{NOW_LEVEL}.txt', MAIN_HERO)
    # player, level_x, level_y = load_level(f'map.txt', MAIN_HERO)

    camera = Camera(level_x, level_y)

    while running:
        time_delta = 1000 / FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # если герой погиб, то просто закрываем игровое окно
                if not player.get_health():
                    running = False
                else:
                    pause = True
                    last_pause = pygame.time.get_ticks()
                    exit_warning(manager, 'Вы уверены, что хотите выйти? '
                                          'Ваш прогресс не сохранится.')
            elif event.type == pygame.KEYDOWN:
                # через события, чтобы вылетал один сюрикен
                if list(player_group) and event.key == pygame.K_RETURN and not pause:
                    player.attack()
                elif event.key == pygame.K_p:
                    pause = not pause
                    if pause:
                        sound_manager.pause_music()
                        last_pause = pygame.time.get_ticks()
                    else:
                        # Добавление упущенного во время паузы времени
                        sound_manager.unpause_music()
                        player.add_paused_time(
                            pygame.time.get_ticks() - last_pause)
                elif event.key == pygame.K_ESCAPE:
                    # если герой погиб, то просто закрываем игровое окно
                    if not player.get_health():
                        running = False
                    else:
                        pause = True
                        last_pause = pygame.time.get_ticks()
                        exit_warning(manager, 'Вы уверены, что хотите выйти? '
                                              'Ваш прогресс не сохранится.')
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    running = False
                # крестик или cancel в диалоговом окне
                if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                    pause = False
                    # Добавление упущенного во время паузы времени
                    player.add_paused_time(
                        pygame.time.get_ticks() - last_pause)
            manager.process_events(event)

        manager.update(time_delta)

        if player.is_win():
            # после окончания игры удаляем спрайты
            for sprite in all_sprites:
                sprite.kill()
            SoundManager.play_victory()
            with open('log.txt') as file:
                max_level = int(file.read())
            if NOW_LEVEL == max_level:
                with open('log.txt', 'w') as file:
                    file.write(str(NOW_LEVEL + 1))
            level_complete_screen()
            return

        game_screen.fill(pygame.Color("light blue"))
        if not pause:
            screen.fill(pygame.Color("#11A550"))

            all_sprites.update()

            if player.get_health():
                # изменяем ракурс камеры
                camera.update(player)
            elif not list(player_group):  # спрайт героя исчез

                # после окончания игры удаляем спрайты
                for sprite in all_sprites:
                    sprite.kill()
                level_complete_screen(win=False)
                return

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            if not issubclass(type(sprite), Enemy) and not isinstance(sprite,
                                                                      MainHero):
                game_screen.blit(sprite.image, camera.apply(sprite))

        # рисуем врагов отдельно, чтобы они не были над другими текстурами
        for sprite in enemies_group:
            game_screen.blit(sprite.image, camera.apply(sprite))

        game_screen.blit(player.image, camera.apply(player))

        screen.blit(game_screen, (0, TILE_SIDE))
        if not pause:
            draw_top_bar()

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)
    # после окончания игры удаляем спрайты
    for sprite in all_sprites:
        sprite.kill()
    pygame.display.set_caption('Меню')

    sound_manager.play_menu_music()


if __name__ == '__main__':
    menu_screen()
