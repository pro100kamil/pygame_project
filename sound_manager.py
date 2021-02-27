from pygame.mixer import Sound, music
from pygame import mixer


mixer.init()


class SoundManager:
    """Звуковой менеджер"""

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

    def __init__(self):
        self.sound = True  # Изначально звук включен
        self.sounds['move_on_ground'].set_volume(0.2)
        self.sounds['fruit'].set_volume(0.2)
        self.sounds['hit'].set_volume(0.2)
        self.sounds['potion'].set_volume(0.2)

    def switch(self):
        """Смена режима звука (включен / выключен)"""
        self.sound = not self.sound

        if self.sound:
            self.start_sound()
        else:
            self.mute_all_sounds()

    def start_sound(self):
        """Включение звука в игре"""

        music.unpause()
        for k, v in self.sounds.items():
            if k in {'move_on_ground', 'fruit', 'hit', 'potion'}:
                v.set_volume(0.2)
            else:
                v.set_volume(1)

    def mute_all_sounds(self):
        """Отключение звука в игре"""

        music.pause()
        for v in self.sounds.values():
            v.set_volume(0)

    def play_shuriken(self):
        """Проигрывание звука сюрикена"""

        self.sounds['shuriken'].play()

    def play_hit(self):
        """Проигрывание звука: ГГ ударил врага"""

        self.sounds['hit'].play()

    def play_fruit_collected(self):
        """Проигрывание звука собранного фрукта"""

        self.sounds['fruit'].play()

    def play_backpack_collected(self):
        """Проигрывание звука собранного рюкзака"""

        self.sounds['backpack'].play()

    def play_got_hit(self):
        """Проигрывание звука: враг ударил ГГ"""

        self.sounds['got_hit'].play()

    def play_move_on_ground(self):
        """Проигрывание звука шагов ГГ"""

        if self.sounds['move_on_ground'].get_num_channels() == 0:
            self.sounds['move_on_ground'].play()

    def play_jump(self):
        """Проигрывание звука прыжка ГГ"""

        self.sounds['jump'].play()

    def play_land(self):
        """Проигрывание звука приземления ГГ"""

        self.sounds['land'].play()

    def play_potion_collected(self):
        """Проигрывание звука собранного зелья"""

        self.sounds['potion'].play()

    def play_voice_game_over(self):
        """Проигрывание голоса "Game Over" при проигрыше уровня"""

        if self.sounds['game_over_sound'].get_num_channels() == 0:
            self.sounds['game_over_voice'].play()

    def play_sound_game_over(self):
        """Проигрывание мелодии при проигрыше уровня"""

        music.stop()
        self.sounds['game_over_sound'].play()

    def play_game_over(self):
        """Проигрывание мелодии и голоса вместе при проигрыше уровня"""

        music.fadeout(500)
        self.sounds['game_over'].play()

    def play_menu_music(self):
        """Проигрывание музыки во время нахождения в меню"""

        if self.sound:
            for sound in self.sounds.values():
                sound: Sound
                sound.stop()
            music.unpause()
            music.unload()
            music.load('music/background.mp3')
            music.set_volume(1)
            music.play(-1)

    def play_game_music(self):
        """Проигрывание музыки во время нахождения в игре"""

        if self.sound:
            for sound in self.sounds.values():
                sound: Sound
                sound.stop()

            music.unpause()
            music.unload()
            music.load('music/background_tango_short.wav')
            music.set_volume(0.1)
            music.play(-1)

    def play_victory(self):
        """Проигрывание мелодии при успешном прохождении уровня"""

        music.fadeout(500)
        self.sounds['victory'].play()

    def update(self):
        pass
