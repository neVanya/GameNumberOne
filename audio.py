"""
audio.py - Управление звуками игры
"""
import pygame
import math
import random


class AudioManager:
    """Менеджер звуков"""

    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.volume = 0.7

    def initialize(self):
        """Создание звуков"""
        try:
            self.create_simple_sounds()
            print("Звуки созданы успешно")
        except Exception as e:
            print(f"Ошибка создания звуков: {e}")
            self.sounds = {}

    def create_simple_sounds(self):
        """Создание простых звуков"""
        # Прыжок - короткий высокий звук
        self.sounds["jump"] = self.create_sound(600, 0.1)

        # Монетка - звонкий звук
        self.sounds["coin"] = self.create_sound(800, 0.08)

        # Смерть врага - низкий звук
        self.sounds["enemy_death"] = self.create_sound(300, 0.2)

        # Урон - неприятный звук
        self.sounds["hurt"] = self.create_sound(200, 0.3)

        # Победа - радостный звук
        self.sounds["win"] = self.create_sound(1000, 0.5)

    def create_sound(self, frequency, duration):
        """Создание простого звука"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))

        buf = bytearray(n_samples * 2)

        for i in range(n_samples):
            t = float(i) / sample_rate
            # Плавное затухание
            envelope = 1.0 - (t / duration)
            sine = int(32767.0 * 0.3 * envelope * math.sin(2.0 * math.pi * frequency * t))

            buf[2 * i] = sine & 0xff
            buf[2 * i + 1] = (sine >> 8) & 0xff

        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(self.volume)
        return sound

    def play_music(self):
        """Запуск простой фоновой музыки"""
        if not self.music_playing:
            try:
                # Создаем простую музыку прямо в памяти
                sample_rate = 22050
                duration = 10.0  # 10 секунд петли
                n_samples = int(round(duration * sample_rate))

                buf = bytearray(n_samples * 2)

                # Простая мелодия
                for i in range(n_samples):
                    t = float(i) / sample_rate

                    # Основная мелодия (синусоида)
                    freq = 440.0  # Ля первой октавы
                    wave1 = 0.1 * math.sin(2.0 * math.pi * freq * t)

                    # Басс (октавой ниже)
                    wave2 = 0.05 * math.sin(2.0 * math.pi * freq * 0.5 * t)

                    # Ритм
                    drum = 0
                    if int(t * 2) % 2 == 0:  # Каждые 0.5 секунды
                        drum = 0.05 * random.random() * math.exp(-(t % 0.5) * 10)

                    mixed = wave1 + wave2 + drum
                    sample = int(32767.0 * mixed)
                    sample = max(-32768, min(32767, sample))

                    buf[2 * i] = sample & 0xff
                    buf[2 * i + 1] = (sample >> 8) & 0xff

                # Создаем звук из буфера
                music_sound = pygame.mixer.Sound(buffer=bytes(buf))
                music_sound.set_volume(self.volume * 0.3)

                # Воспроизводим в цикле
                music_sound.play(loops=-1)
                self.music_playing = True

            except Exception as e:
                print(f"Не удалось воспроизвести музыку: {e}")

    def stop_music(self):
        """Остановка музыки"""
        pygame.mixer.music.stop()
        self.music_playing = False

    def play_sound(self, name):
        """Воспроизведение звука"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass

    def set_volume(self, volume):
        """Установка громкости"""
        self.volume = max(0.0, min(1.0, volume))

        # Обновляем громкость всех звуков
        for sound in self.sounds.values():
            sound.set_volume(self.volume)


# Глобальный экземпляр
audio_manager = AudioManager()