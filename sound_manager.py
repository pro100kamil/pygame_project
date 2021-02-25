from pygame.mixer import Sound, music
from pygame import mixer

mixer.init()


class SoundManager:
    sounds = {'shuriken': Sound('sounds/shuriken_flight.mp3'),

              'hit': Sound('sounds/hit.wav'),

              'fruit': Sound('sounds/fruit.wav'),

              'backpack': Sound('sounds/backpack.wav'),

              'got_hit': Sound('sounds/ouch.wav'),

              'move_on_ground': Sound('sounds/move_on_ground.wav'),

              'jump': Sound('sounds/jump.wav')}

    sounds['move_on_ground'].set_volume(0.2)
    sounds['fruit'].set_volume(0.2)
    sounds['hit'].set_volume(0.2)

    music.load('music/background.mp3')
    music.play(-1)
    music.set_volume(0.2)

    @staticmethod
    def play_shuriken():
        SoundManager.sounds['shuriken'].play()

    @staticmethod
    def play_hit():
        SoundManager.sounds['hit'].play()

    @staticmethod
    def play_fruit_collected():
        SoundManager.sounds['fruit'].play()

    @staticmethod
    def play_backpack_collected():
        SoundManager.sounds['backpack'].play()

    @staticmethod
    def fade_out_music(time: int):
        music.fadeout(time)

    @staticmethod
    def stop_music():
        music.stop()

    @staticmethod
    def play_music():
        music.play()

    def update(self):
        pass

    @staticmethod
    def play_got_hit():
        SoundManager.sounds['got_hit'].play()

    @staticmethod
    def play_move_on_ground():
        if SoundManager.sounds['move_on_ground'].get_num_channels() == 0:
            SoundManager.sounds['move_on_ground'].play()

    @staticmethod
    def play_jump():
        SoundManager.sounds['jump'].play()