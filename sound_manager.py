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

    def __init__(self):
        self.sound = True
        self.sounds['move_on_ground'].set_volume(0.2)
        self.sounds['fruit'].set_volume(0.2)
        self.sounds['hit'].set_volume(0.2)
        self.sounds['potion'].set_volume(0.2)

    def switch(self):
        self.sound = not self.sound

        if self.sound:
            self.start_sound()
        else:
            self.mute_all_sounds()

    def start_sound(self):
        """Включает звук в игре"""
        music.unpause()
        for k, v in self.sounds.items():
            if k in {'move_on_ground', 'fruit', 'hit', 'potion'}:
                v.set_volume(0.2)
            else:
                v.set_volume(1)

    def mute_all_sounds(self):
        """Отключает звук в игре"""
        music.pause()
        for v in self.sounds.values():
            v.set_volume(0)

    def play_shuriken(self):
        self.sounds['shuriken'].play()

    def play_hit(self):
        self.sounds['hit'].play()

    def play_fruit_collected(self):
        self.sounds['fruit'].play()

    def play_backpack_collected(self):
        self.sounds['backpack'].play()

    def play_got_hit(self):
        self.sounds['got_hit'].play()

    def play_move_on_ground(self):
        if self.sounds['move_on_ground'].get_num_channels() == 0:
            self.sounds['move_on_ground'].play()

    def play_jump(self):
        self.sounds['jump'].play()

    def play_land(self):
        self.sounds['land'].play()

    def play_potion_collected(self):
        self.sounds['potion'].play()

    def play_voice_game_over(self):
        if self.sounds['game_over_sound'].get_num_channels() == 0:
            self.sounds['game_over_voice'].play()

    def play_sound_game_over(self):
        music.stop()
        self.sounds['game_over_sound'].play()

    def play_game_over(self):
        music.fadeout(500)
        self.sounds['game_over'].play()

    def play_menu_music(self):
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
        music.fadeout(500)
        self.sounds['victory'].play()

    def update(self):
        pass
