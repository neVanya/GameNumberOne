import pygame
import math
import random
from settings import *
from animations import create_coin_animations


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, value=10, coin_type="normal"):
        super().__init__()

        self.value = value
        self.coin_type = coin_type
        self.animations = create_coin_animations()
        self.image = self.animations["spin"].get_current_image()

        # Для анимации парения - фиксированная начальная позиция
        self.base_y = y  # Запоминаем исходную позицию
        self.float_offset = random.random() * 2 * math.pi
        self.float_speed = 0.05
        self.float_amplitude = 2

        # Создаем прямоугольник для позиции
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Для сбора
        self.collected = False
        self.collect_timer = 0
        self.collect_duration = 20

        # Сохраняем оригинальное изображение для анимации сбора
        self.original_image = self.image.copy()

    def update(self):
        """Анимация парения и вращения"""
        if not self.collected:
            # Обновление анимаций
            self.animations["spin"].update()
            self.animations["glow"].update()

            # Комбинируем анимации
            spin_img = self.animations["spin"].get_current_image()
            glow_img = self.animations["glow"].get_current_image()

            # Создаем новое изображение
            self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
            self.image.blit(spin_img, (0, 0))
            self.image.blit(glow_img, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

            # Парение вокруг base_y
            self.float_offset += self.float_speed
            float_y = math.sin(self.float_offset) * self.float_amplitude
            self.rect.y = self.base_y + float_y

            # Сохраняем оригинальное изображение
            self.original_image = self.image.copy()
        else:
            # Анимация сбора
            self.collect_timer += 1
            if self.collect_timer < self.collect_duration:
                # Увеличение и исчезновение
                scale = 1 + (self.collect_timer / self.collect_duration) * 2
                alpha = int(255 * (1 - self.collect_timer / self.collect_duration))

                # Масштабируем оригинальное изображение
                orig_size = self.original_image.get_size()
                new_size = (int(orig_size[0] * scale), int(orig_size[1] * scale))

                # Создаем новую поверхность с альфа-каналом
                scaled = pygame.transform.scale(self.original_image, new_size)

                # Создаем поверхность с альфа-каналом для прозрачности
                self.image = pygame.Surface(new_size, pygame.SRCALPHA)
                scaled_with_alpha = scaled.copy()
                scaled_with_alpha.set_alpha(alpha)
                self.image.blit(scaled_with_alpha, (0, 0))

                # Обновляем rect с сохранением центра
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
            else:
                self.kill()

    def collect(self):
        """Вызывается при сборе монетки"""
        if not self.collected:
            self.collected = True
            self.collect_timer = 0

            # Звук сбора
            from audio import audio_manager
            audio_manager.play_sound("coin")

            # Эффект частиц
            from particles import create_collect_effect
            return create_collect_effect(self.rect.centerx, self.rect.centery, self.coin_type)
        return None