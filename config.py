"""
config.py - Конфигурация и инициализация игры
"""
import pygame


class GameConfig:
    """Класс для управления конфигурацией игры"""
    _initialized = False

    @classmethod
    def initialize(cls):
        """Инициализация всех систем Pygame"""
        if not cls._initialized:
            # Инициализируем основные модули Pygame
            pygame.init()

            # Инициализируем аудио систему
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

            # Инициализируем шрифты
            pygame.font.init()

            cls._initialized = True
            print("Pygame инициализирован")

    @classmethod
    def is_initialized(cls):
        """Проверка инициализации"""
        return cls._initialized

    @classmethod
    def quit(cls):
        """Завершение всех систем Pygame"""
        if cls._initialized:
            pygame.mixer.quit()
            pygame.font.quit()
            pygame.quit()
            cls._initialized = False
            print("Pygame завершен")


# Глобальный конфиг
config = GameConfig()