import pygame
import random
import math
from settings import *


class Particle:
    """Одна частица"""

    def __init__(self, x, y, color, velocity_x=0, velocity_y=0,
                 lifetime=60, size=3, gravity=0.1, fade=True):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.fade = fade
        self.alive = True

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        if self.fade:
            # Плавное исчезновение
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = (*self.color[:3], alpha) if len(self.color) == 4 else self.color
            if len(color) == 4:
                surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (self.size, self.size), self.size)
                screen.blit(surf, (self.x - self.size, self.y - self.size))
            else:
                pygame.draw.circle(screen, color,
                                   (int(self.x), int(self.y)), self.size)
        else:
            pygame.draw.circle(screen, self.color,
                               (int(self.x), int(self.y)), self.size)


class ParticleSystem:
    """Система частиц"""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10, color=WHITE,
             min_velocity=(-2, -2), max_velocity=(2, 0),
             lifetime_range=(30, 60), size_range=(2, 5)):
        """Создание вспышки частиц"""
        for _ in range(count):
            velocity_x = random.uniform(min_velocity[0], max_velocity[0])
            velocity_y = random.uniform(min_velocity[1], max_velocity[1])
            lifetime = random.randint(lifetime_range[0], lifetime_range[1])
            size = random.randint(size_range[0], size_range[1])

            particle = Particle(x, y, color, velocity_x, velocity_y,
                                lifetime, size)
            self.particles.append(particle)

    def emit_circle(self, x, y, count=20, color=WHITE,
                    speed=2, lifetime=40):
        """Создание кругового взрыва частиц"""
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed

            particle = Particle(x, y, color, velocity_x, velocity_y,
                                lifetime, size=2)
            self.particles.append(particle)

    def emit_fountain(self, x, y, count=5, color=WHITE,
                      speed=3, lifetime=50):
        """Создание фонтана частиц (для прыжков)"""
        for _ in range(count):
            velocity_x = random.uniform(-1, 1)
            velocity_y = random.uniform(-speed, -speed * 0.5)

            particle = Particle(x, y, color, velocity_x, velocity_y,
                                lifetime, size=random.randint(1, 3))
            self.particles.append(particle)

    def update(self):
        """Обновление всех частиц"""
        for particle in self.particles[:]:
            particle.update()
            if not particle.alive:
                self.particles.remove(particle)

    def draw(self, screen):
        """Отрисовка всех частиц"""
        for particle in self.particles:
            particle.draw(screen)


# Предустановленные эффекты
def create_collect_effect(x, y, coin_type="normal"):
    """Эффект сбора монетки"""
    system = ParticleSystem()

    if coin_type == "normal":
        color = (255, 215, 0)  # Золотой
    elif coin_type == "silver":
        color = (192, 192, 192)  # Серебряный
    elif coin_type == "gold":
        color = (255, 140, 0)  # Оранжевое золото
    else:
        color = WHITE

    system.emit_circle(x, y, count=15, color=color, speed=3, lifetime=30)
    return system


def create_jump_effect(x, y):
    """Эффект прыжка"""
    system = ParticleSystem()
    system.emit_fountain(x, y, count=8, color=(200, 200, 255),
                         speed=4, lifetime=40)
    return system


def create_enemy_death_effect(x, y):
    """Эффект смерти врага"""
    system = ParticleSystem()
    system.emit(x, y, count=20, color=RED,
                min_velocity=(-3, -3), max_velocity=(3, 3),
                lifetime_range=(20, 40), size_range=(2, 4))
    return system


def create_hit_effect(x, y):
    """Эффект получения урона"""
    system = ParticleSystem()
    system.emit_circle(x, y, count=10, color=RED, speed=2, lifetime=20)
    return system