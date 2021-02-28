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
    return pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((WIDTH // 2 - 150, HEIGHT // 2 - 100),
                         (300, 200)),
        manager=manager,
        window_title='Подтверждение',
        action_long_desc=msg,
        action_short_name='OK',
        blocking=True
    )


def menu_screen():
    """Открывает окно меню и возращает имя героя и номер выбранного уровня"""
    global MAIN_HERO

    sound_manager.play_menu_music()

    dialog = None  # текущее открытое диалоговое окно

    pygame.display.set_caption('Меню')

    list_heroes = list(HEROES.keys())
    now = 0  # индекс текущего героя
    MAIN_HERO = list_heroes[now]
    # координаты и размер изображения главного героя
    size_hero_image = 300, 300
    coord_hero_image = (WIDTH - size_hero_image[0]) // 2, 50
    image = pygame.transform.scale(load_image("for menu/Ninja Frog.png"),
                                   size_hero_image)

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')
    # расставляем кнопки и лейблы
    width, height = 31, 33
    x, y = coord_hero_image[0] + (size_hero_image[0] - width) // 2, 10
    volume = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(x, y, width, height),
        text='',
        tool_tip_text='Нажмите, чтобы включить/выключить звук',
        object_id='#volume',
        manager=manager
    )

    width, height = 180, 50
    x = coord_hero_image[0] + (size_hero_image[0] - width) // 2
    y = coord_hero_image[1] + size_hero_image[1] + 20
    name_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y, width, height),
        text='Ninja Frog',
        manager=manager
    )
    damage_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + height, width, height),
        text=f'Урон: {HEROES["Ninja Frog"].damage}',
        manager=manager
    )
    speed_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + 2 * height, width, height),
        text=f'Скорость: {HEROES["Ninja Frog"].speed}',
        manager=manager
    )
    health_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y + 3 * height, width, height),
        text=f'Жизни: {HEROES["Ninja Frog"].health}',
        manager=manager
    )

    width_play, height_play = 200, 80
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
                if dialog is None:
                    dialog = exit_warning(manager)
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
                    # чтобы не открывалось несколько диалогов
                    if dialog is None:
                        dialog = exit_warning(manager)
                MAIN_HERO = list_heroes[now]
                image = pygame.transform.scale(
                    load_image(f"for menu/{MAIN_HERO}.png"), size_hero_image)
                name_label.set_text(MAIN_HERO)
                damage_label.set_text(
                    f'Урон: {HEROES[MAIN_HERO].damage}')
                speed_label.set_text(
                    f'Скорость: {HEROES[MAIN_HERO].speed}')
                health_label.set_text(
                    f'Жизни: {HEROES[MAIN_HERO].health}')
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    terminate()
                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play:
                        print('PLAY')
                        level_selection_screen()
                    elif event.ui_element == volume:
                        sound_manager.switch()
                # крестик или cancel в диалоговом окне
                elif event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                    dialog = None
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

    dialog = None  # текущее открытое диалоговое окно

    images = []  # изображения номеров уровней
    size = 80, 80
    for i in range(1, KOL_LEVELS + 1):
        images.append(pygame.transform.scale(
            load_image(f"for menu/Levels/{str(i).rjust(2, '0')}.png"), size))
    rects = []  # прямоугольники, в которых лежат изображения
    delta = 50
    y = (HEIGHT - size[1] * 2 - delta) // 2
    x0 = (WIDTH - size[0] * KOL_LEVELS // 2) // 2
    for i in range(KOL_LEVELS // 2):
        x = x0 + size[0] * i
        rects.append(pygame.Rect(x, y, *size))
    y += size[1] + delta
    for i in range(KOL_LEVELS // 2, KOL_LEVELS):
        x = x0 + size[0] * (i - KOL_LEVELS // 2)
        rects.append(pygame.Rect(x, y, *size))

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')
    # расставляем кнопки и лейблы
    width, height = 31, 33
    x, y = 10, 10
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
                                with open('level.txt') as file:
                                    max_level = int(file.read())
                                if i <= max_level:
                                    NOW_LEVEL = i
                                    game()
                                    return
                                else:
                                    # чтобы не открывалось несколько диалогов
                                    if dialog is None:
                                        # окно с предупреждением
                                        dialog = pygame_gui.windows.UIMessageWindow(
                                            rect=pygame.Rect(
                                                WIDTH // 2 - 150,
                                                HEIGHT // 2 + 150, 300, 300),
                                            html_message='Этот уровень вам '
                                                         'недоступен',
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
                # крестик или cancel в диалоговом окне
                elif event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                    dialog = None
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(pygame.Color('#E5D007'))

        font = pygame.font.SysFont("arial", 50)
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


def level_end_screen(win=True):
    """Открывает окно после выигрыша/проигрыша/прохождения игры"""
    global NOW_LEVEL

    manager = pygame_gui.UIManager(SIZE, 'styles/style.json')
    # расставляем кнопки и лейблы
    width, height = 31, 33
    x, y = 10, 10
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

    if win and NOW_LEVEL != KOL_LEVELS:
        # кнопка следующий уровень есть только тогда, когда пользователь
        # прошёл уровень, который не является последним
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

        font = pygame.font.SysFont("arial", 70)
        text = font.render(("Уровень пройден!" if NOW_LEVEL != KOL_LEVELS
                            else "Поздравляем! Вы прошли игру!")
                           if win else "Вы проиграли",
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


def load_level(filename):
    """Загрузка уровня"""
    filename = os.path.join('maps', filename)
    # если файл не существует, то выходим
    if not os.path.isfile(filename):
        raise SystemExit(f"Файл с картой '{filename}' не найден")

    notations = {'@': MainHero,
                 '1': Checkpoint, '9': Checkpoint,
                 '.': Spikes, '~': Saw, '-': Platform,
                 'b': Bunny, 'c': Chicken, 'm': Mushroom, 's': Slime,
                 'o': AngryPig, 'h': Chameleon, 'r': Rino, 'p': Plant,
                 'q': Plant,
                 '*': Fruit, '?': Potion, '+': Backpack
                 }  # обозначения

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    new_player, x, y = None, None, None
    for y, row in enumerate(level_map):
        for x, elem in enumerate(row):
            if elem in notations:
                args = []
                if elem == '@':
                    args.append(MAIN_HERO)
                elif elem == 'q':
                    args.append('left')
                elif elem == 'p':
                    args.append('right')
                elif elem == '1':
                    args.append('Start')
                elif elem == '9':
                    args.append('End')
                w = getattr(notations[elem], "width", TILE_SIDE)
                h = getattr(notations[elem], "height", TILE_SIDE)
                tmp = notations[elem](x * TILE_SIDE - (TILE_SIDE - w),
                                      y * TILE_SIDE + (TILE_SIDE - h), *args)
                if elem == '@':
                    new_player = tmp

    return new_player, (x + 1) * TILE_SIDE, (y + 1) * TILE_SIDE


def game():
    """Открывает основное окно"""
    with open('level.txt') as file:
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

    dialog = None  # текущее открытое диалговое окно

    player, level_x, level_y = load_level(f'level{NOW_LEVEL}.txt')

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
                    if dialog is None:
                        dialog = exit_warning(manager,
                                              'Вы уверены, что хотите выйти? '
                                              'Ваш прогресс на текущем уровне '
                                              'не сохранится.')
            elif event.type == pygame.KEYDOWN:
                # через события, чтобы вылетал один сюрикен
                if list(
                        player_group) and event.key == pygame.K_RETURN and not pause:
                    player.attack()
                elif event.key == pygame.K_p:
                    pause = not pause
                    if pause:
                        sound_manager.mute_all_sounds()
                        last_pause = pygame.time.get_ticks()
                    else:
                        # Добавление упущенного во время паузы времени
                        sound_manager.start_sound()
                        player.add_paused_time(
                            pygame.time.get_ticks() - last_pause)
                elif event.key == pygame.K_ESCAPE:
                    # если герой погиб, то просто закрываем игровое окно
                    if not player.get_health():
                        running = False
                    else:
                        pause = True
                        last_pause = pygame.time.get_ticks()
                        # чтобы не открывалось несколько диалогов
                        if dialog is None:
                            dialog = exit_warning(manager,
                                                  'Вы уверены, что хотите выйти? '
                                                  'Ваш прогресс на текущем уровне '
                                                  'не сохранится.')
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    running = False
                # крестик или cancel в диалоговом окне
                if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                    pause = False
                    dialog = None
                    # Добавление упущенного во время паузы времени
                    player.add_paused_time(
                        pygame.time.get_ticks() - last_pause)
            manager.process_events(event)

        manager.update(time_delta)

        if player.is_win():
            # после окончания игры удаляем спрайты
            for sprite in all_sprites:
                sprite.kill()
            sound_manager.play_victory()
            with open('level.txt') as file:
                max_level = int(file.read())
            if NOW_LEVEL == max_level:
                with open('level.txt', 'w') as file:
                    file.write(str(NOW_LEVEL + 1))
            level_end_screen()
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
                level_end_screen(win=False)
                return

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            if not issubclass(type(sprite), Enemy) and not isinstance(sprite,
                                                                      MainHero):
                game_screen.blit(sprite.image, camera.apply(sprite))

        # рисуем врагов и героя отдельно,
        # чтобы они были над другими текстурами
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
