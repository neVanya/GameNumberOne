import pygame
import math
from settings import *


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="patrol"):
        super().__init__()

        self.enemy_type = enemy_type

        # Создаем изображение врага
        self.image = pygame.Surface((40, 40))

        if enemy_type == "patrol":
            self.image.fill(RED)
        elif enemy_type == "chaser":
            self.image.fill((255, 0, 255))
        elif enemy_type == "shooter":
            self.image.fill((255, 100, 0))

        # Рисуем глаза
        pygame.draw.circle(self.image, WHITE, (10, 10), 6)
        pygame.draw.circle(self.image, WHITE, (30, 10), 6)
        pygame.draw.circle(self.image, BLACK, (10, 10), 3)
        pygame.draw.circle(self.image, BLACK, (30, 10), 3)

        # Рот
        pygame.draw.arc(self.image, BLACK, (10, 20, 20, 15), 3.14, 6.28, 2)

        # Создаем прямоугольник
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Физика
        self.vel_x = 2
        self.vel_y = 0
        self.direction = 1

        # Для патрулирования
        self.patrol_range = 150
        self.start_x = x

        # Для преследования
        self.sight_range = 300
        self.chase_speed = 3

        # Для стрельбы
        self.shoot_cooldown = 0
        self.bullets = pygame.sprite.Group()

        # Жизнь
        self.health = 2 if enemy_type == "chaser" else 1

    def update(self, player=None):
        """Обновление поведения врага"""
        if self.enemy_type == "patrol":
            self.patrol()
        elif self.enemy_type == "chaser" and player:
            self.chase(player)
        elif self.enemy_type == "shooter" and player:
            self.shoot(player)

        # Обновление пуль
        if self.enemy_type == "shooter":
            self.bullets.update()
            self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

    def patrol(self):
        """Патрулирование вперед-назад"""
        self.rect.x += self.vel_x * self.direction

        if self.rect.x > self.start_x + self.patrol_range:
            self.direction = -1
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.rect.x < self.start_x:
            self.direction = 1
            self.image = pygame.transform.flip(self.image, True, False)

    def chase(self, player):
        """Преследование игрока"""
        dx = player.rect.x - self.rect.x
        distance = abs(dx)

        if distance < self.sight_range:
            if dx > 10:
                self.rect.x += self.chase_speed
                self.image = pygame.transform.flip(self.image, True, False)
            elif dx < -10:
                self.rect.x -= self.chase_speed
                self.image = pygame.transform.flip(self.image, False, False)

    def shoot(self, player):
        """Стрельба в игрока"""
        if player and self.shoot_cooldown == 0:
            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 400:
                bullet = Bullet(self.rect.centerx, self.rect.centery,
                                dx / distance * 5, dy / distance * 5)
                self.bullets.add(bullet)
                self.shoot_cooldown = 60

    def take_damage(self):
        """Получение урона"""
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return True
        return False

    def draw_bullets(self, screen):
        """Отрисовка пуль"""
        self.bullets.draw(screen)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        pygame.draw.circle(self.image, (255, 200, 0), (4, 4), 4)

        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.lifetime = 120

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()

        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()