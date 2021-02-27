from pygame.mixer import Sound, music
from pygame import mixer

mixer.init()


class SoundManager:
    sounds = {'shuriken': Sound('sounds/shuriken_flight.mp3'),

              'hit': Sound('sounds/hit.wav'),

              'fruit': Sound('sounds/fruit.wav'),

              'backpack': Sound('sounds/backpack.wav'),

              'got_hit': Sound('sounds/oof.wav'),

              'move_on_ground': Sound('sounds/move_on_ground.wav'),

              'jump': Sound('sounds/jump.wav'),

              'land': Sound('sounds/land.wav'),

              'potion': Sound('sounds/potion.wav'),

              'game_over_sound': Sound('sounds/sound_game_over.wav'),

              'game_over_voice': Sound('sounds/voice_game_over.mp3'),

              'game_over': Sound('sounds/game_over_finally.wav'),

              'victory': Sound('sounds/sound_victory.wav')}

    sounds['move_on_ground'].set_volume(0.2)
    sounds['fruit'].set_volume(0.2)
    sounds['hit'].set_volume(0.2)
    sounds['potion'].set_volume(0.2)

    @staticmethod
    def start_sound():
        """Включает звук в игре"""
        SoundManager.play_menu_music()
        for k, v in SoundManager.sounds.items():
            if k in {'move_on_ground', 'fruit', 'hit', 'potion'}:
                v.set_volume(0.2)
            else:
                v.set_volume(1)

    @staticmethod
    def remove_sound():
        """Отключает звук в игре"""
        music.set_volume(0)
        for v in SoundManager.sounds.values():
            v.set_volume(0)

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
    def pause_music():
        music.pause()

    @staticmethod
    def unpause_music():
        music.unpause()

    @staticmethod
    def play_music():
        music.play()

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

    @staticmethod
    def play_land():
        SoundManager.sounds['land'].play()

    @staticmethod
    def play_potion_collected():
        SoundManager.sounds['potion'].play()

    @staticmethod
    def play_voice_game_over():
        if SoundManager.sounds['game_over_sound'].get_num_channels() == 0:
            SoundManager.sounds['game_over_voice'].play()

    @staticmethod
    def play_sound_game_over():
        mixer.music.stop()
        SoundManager.sounds['game_over_sound'].play()

    @staticmethod
    def play_game_over():
        mixer.music.fadeout(500)
        SoundManager.sounds['game_over'].play()

    @staticmethod
    def play_menu_music():
        for sound in SoundManager.sounds.values():
            sound: Sound
            sound.stop()
        mixer.music.fadeout(500)
        mixer.music.unload()
        mixer.music.load('music/background.mp3')
        mixer.music.set_volume(1)
        mixer.music.play(-1)

    @staticmethod
    def play_game_music():
        for sound in SoundManager.sounds.values():
            sound: Sound
            sound.stop()
        mixer.music.fadeout(500)
        mixer.music.unload()
        mixer.music.load('music/background_tango_short.wav')
        music.set_volume(0.3)
        mixer.music.play(-1)

    @staticmethod
    def play_victory():
        mixer.music.fadeout(500)
        SoundManager.sounds['victory'].play()

    def update(self):
        pass
