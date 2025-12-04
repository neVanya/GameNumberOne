import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Создаем изображение игрока
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)

        # Рисуем лицо
        pygame.draw.circle(self.image, WHITE, (10, 15), 5)
        pygame.draw.circle(self.image, WHITE, (30, 15), 5)
        pygame.draw.arc(self.image, WHITE, (10, 25, 20, 15), 0, 3.14, 2)

        # Создаем прямоугольник для позиции и столкновений
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Физика
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True

    def update(self):
        """Обновление позиции (без проверки столкновений)"""
        # Применяем гравитацию
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x

        # Ограничение по краям экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True

    def handle_collisions(self, platforms):
        """Обработка столкновений с платформами"""
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Столкновение сверху (падаем на платформу)
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # Столкновение снизу (прыгаем в платформу)
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                # Столкновение сбоку
                elif self.vel_x != 0:
                    if self.vel_x > 0:  # Движемся вправо
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:  # Движемся влево
                        self.rect.left = platform.rect.right

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False

    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.facing_right = True

    def stop(self):
        self.vel_x = 0