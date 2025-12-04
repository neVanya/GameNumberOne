import pygame
from settings import *


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="ground"):
        super().__init__()

        self.platform_type = platform_type

        # Создаем изображение платформы
        self.image = pygame.Surface((width, height))

        # Разные цвета для разных типов платформ
        if platform_type == "ground":
            self.image.fill(GREEN)
        elif platform_type == "moving":
            self.image.fill((200, 100, 50))
        elif platform_type == "bouncing":
            self.image.fill((255, 215, 0))
        else:
            self.image.fill(GREEN)

        # Рамка
        pygame.draw.rect(self.image, BLACK, (0, 0, width, height), 2)

        # Создаем прямоугольник для позиции
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Для движущихся платформ
        self.speed = 2 if platform_type == "moving" else 0
        self.move_range = 100 if platform_type == "moving" else 0
        self.start_x = x
        self.direction = 1

    def update(self):
        """Обновление для движущихся платформ"""
        if self.platform_type == "moving":
            self.rect.x += self.speed * self.direction

            if self.rect.x > self.start_x + self.move_range:
                self.direction = -1
            elif self.rect.x < self.start_x:
                self.direction = 1