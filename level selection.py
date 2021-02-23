import pygame

pygame.init()
pygame.display.set_caption('Level selection')
SIZE = WIDTH, HEIGHT = 750, 750
screen = pygame.display.set_mode(SIZE)
fps = 30
kol_levels = 10

if __name__ == "__main__":

    clock = pygame.time.Clock()
    images = []
    size = 80, 80
    for i in range(1, kol_levels + 1):
        images.append(pygame.transform.scale(
            pygame.image.load(f"Levels/{str(i).rjust(2, '0')}.png"), size))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass

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

        delta = 50
        y = (HEIGHT - size[1] * 2 - delta) // 2
        x0 = (WIDTH - size[0] * kol_levels // 2) // 2
        for i in range(kol_levels // 2):
            x = x0 + size[0] * i
            screen.blit(images[i], (x, y, *size))
            if i == 4:
                y += size[1] + delta
        for i in range(kol_levels // 2, kol_levels):
            x = x0 + size[0] * (i - kol_levels // 2)
            screen.blit(images[i], (x, y, *size))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
