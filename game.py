from enemy import *
from main_character import MainHero
from some_classes import *


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
                # Spikes(x * TILE_SIDE, y * TILE_SIDE)
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
                Bunny(x * TILE_SIDE, y * TILE_SIDE, 10)
            elif elem == 'm':
                Mushroom(x * TILE_SIDE, y * TILE_SIDE, -3.5, 100)
            elif elem == 's':
                Slime(x * TILE_SIDE, y * TILE_SIDE, -1, 100)
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


def game(MAIN_HERO, level_num):
    pygame.display.set_caption('Игра')
    # запуск без меню
    # MAIN_HERO = 'Virtual Guy'
    # level_num = 1

    running = True
    pause = False
    last_pause = 0

    player, level_x, level_y = load_level(f'level{level_num}.txt', MAIN_HERO)
    # player, level_x, level_y = load_level(f'map.txt', MAIN_HERO)

    camera = Camera(level_x, level_y)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # через события, чтобы вылетал один сюрикен
                if event.key == pygame.K_RETURN and not pause:
                    player.attack()
                elif event.key == pygame.K_p:
                    pause = not pause
                    if pause:
                        last_pause = pygame.time.get_ticks()
                    else:
                        # Добавление упущенного во время паузы времени
                        player.add_paused_time(
                            pygame.time.get_ticks() - last_pause)
        if pause:
            continue

        game_screen.fill(pygame.Color("light blue"))
        screen.fill(pygame.Color("#11A550"))

        all_sprites.update()

        if player.health:
            # изменяем ракурс камеры
            camera.update(player)
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

        draw_top_bar()

        pygame.display.flip()
        clock.tick(FPS)

    # после окончания игры удаляем спрайты
    for sprite in all_sprites:
        sprite.kill()

    pygame.display.set_caption('Меню')