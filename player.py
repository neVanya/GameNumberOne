import pygame
from settings import *
from animations import create_player_animations
from particles import create_jump_effect


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Анимации
        self.animations = create_player_animations()
        self.current_animation = "idle"
        self.image = self.animations[self.current_animation].get_current_image()

        # Создаем прямоугольник для позиции и столкновений
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Физика
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True

        # Для анимаций
        self.last_animation = "idle"
        self.jump_pressed = False

    def update(self):
        """Обновление позиции и анимации"""
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

        # Обновление анимации
        self.update_animation()
        self.animations[self.current_animation].update()

        # Получаем текущий кадр
        self.image = self.animations[self.current_animation].get_current_image()

        # Отражение при движении влево
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update_animation(self):
        """Обновление текущей анимации"""
        if not self.on_ground:
            self.current_animation = "jump"
            if self.animations["jump"].done:
                self.animations["jump"].reset()
        elif abs(self.vel_x) > 0.5:
            self.current_animation = "run"
        else:
            self.current_animation = "idle"

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

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            self.animations["jump"].reset()

            # Эффект прыжка (частицы)
            return create_jump_effect(self.rect.centerx, self.rect.bottom)
        return None

    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False

    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.facing_right = True

    def stop(self):
        self.vel_x = 0