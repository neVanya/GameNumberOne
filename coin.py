import pygame
import math
from settings import *


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, value=10, coin_type="normal"):
        super().__init__()

        self.value = value
        self.coin_type = coin_type
        self.animation_time = 0
        self.collected = False

        # Создаем изображение монетки
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)

        # Цвета для разных типов монет
        if coin_type == "normal":
            self.color = (255, 215, 0)
        elif coin_type == "silver":
            self.color = (192, 192, 192)
        elif coin_type == "gold":
            self.color = (255, 140, 0)
            self.value = 50

        # Рисуем монетку
        pygame.draw.circle(self.image, self.color, (12, 12), 10)
        pygame.draw.circle(self.image, (255, 255, 200), (12, 12), 6)
        pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 3)

        # Создаем прямоугольник для позиции
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Для анимации
        self.float_offset = 0
        self.float_speed = 0.05

    def update(self):
        """Анимация парения"""
        if not self.collected:
            self.float_offset += self.float_speed
            self.rect.y += math.sin(self.float_offset) * 0.5

    def collect(self):
        """Вызывается при сборе монетки"""
        self.collected = True
        self.kill()