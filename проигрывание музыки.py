import sys
import pygame

pygame.init()
sc = pygame.display.set_mode((400, 300))

pygame.mixer.music.load('music/song.mp3')  # фоновая музыка (надо будет поменять)
pygame.mixer.music.play(-1)  # -1 - циклическое проигрывание

sound1 = pygame.mixer.Sound('sounds/shuriken_flight.mp3')  # гг выпустил сюрикен
sound2 = pygame.mixer.Sound('sounds/проигрыш.mp3')  # гг погиб


if __name__ == "__main__":
    running = True
    pause = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = not pause
                    if pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_UP:
                    pygame.mixer.music.set_volume(1)
                elif event.key == pygame.K_DOWN:
                    pygame.mixer.music.fadeout(2000)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # левая кнопка мыши
                    sound1.play()
                elif event.button == 3:  # правая кнопка мыши
                    sound2.play()

    pygame.quit()
