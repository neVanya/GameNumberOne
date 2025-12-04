import pygame
from settings import *


class Animation:
    """Базовый класс для анимаций"""

    def __init__(self, images, speed=0.1, loop=True):
        self.images = images
        self.speed = speed
        self.loop = loop
        self.frame = 0
        self.done = False

    def update(self):
        if not self.done:
            self.frame += self.speed
            if self.frame >= len(self.images):
                if self.loop:
                    self.frame = 0
                else:
                    self.frame = len(self.images) - 1
                    self.done = True

    def get_current_image(self):
        return self.images[int(self.frame) % len(self.images)]

    def reset(self):
        self.frame = 0
        self.done = False


class SpriteSheet:
    """Загрузка и нарезка спрайт-листов"""

    def __init__(self, filename, frame_width, frame_height):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.rows = self.sheet.get_height() // frame_height
        self.cols = self.sheet.get_width() // frame_width

    def get_frames(self, row=0, start_col=0, num_frames=None):
        """Получение кадров анимации из строки спрайт-листа"""
        frames = []
        if num_frames is None:
            num_frames = self.cols - start_col

        for col in range(start_col, start_col + num_frames):
            frame = self.sheet.subsurface(
                pygame.Rect(col * self.frame_width,
                            row * self.frame_height,
                            self.frame_width,
                            self.frame_height))
            frames.append(frame)

        return frames

    def get_frame(self, row, col):
        """Получение одного кадра"""
        return self.sheet.subsurface(
            pygame.Rect(col * self.frame_width,
                        row * self.frame_height,
                        self.frame_width,
                        self.frame_height))


# Создаем простые анимации через код (если нет спрайт-листов)
def create_player_animations():
    """Создание анимаций игрока через код"""
    animations = {}

    # Анимация покоя
    idle_frames = []
    for i in range(4):
        surf = pygame.Surface((40, 60), pygame.SRCALPHA)
        surf.fill(BLUE)
        # Моргание глаз
        eye_y = 15 if i % 4 < 2 else 16
        pygame.draw.circle(surf, WHITE, (10, eye_y), 5)
        pygame.draw.circle(surf, WHITE, (30, eye_y), 5)
        pygame.draw.circle(surf, BLACK, (10, eye_y), 2)
        pygame.draw.circle(surf, BLACK, (30, eye_y), 2)

        # Улыбка
        smile_y = 35 if i % 4 < 2 else 36
        pygame.draw.arc(surf, WHITE, (10, 25, 20, 15), 0, 3.14, 2)
        idle_frames.append(surf)

    animations["idle"] = Animation(idle_frames, speed=0.1)

    # Анимация бега
    run_frames = []
    for i in range(6):
        surf = pygame.Surface((40, 60), pygame.SRCALPHA)
        surf.fill(BLUE)

        # Ноги в разных позициях
        leg_offset = i * 5 % 15
        pygame.draw.rect(surf, (80, 120, 200),
                         (10, 50, 8, 10 + leg_offset))
        pygame.draw.rect(surf, (80, 120, 200),
                         (22, 50, 8, 10 - leg_offset))

        # Голова
        pygame.draw.circle(surf, WHITE, (10, 15), 5)
        pygame.draw.circle(surf, WHITE, (30, 15), 5)
        pygame.draw.circle(surf, BLACK, (10, 15), 2)
        pygame.draw.circle(surf, BLACK, (30, 15), 2)

        # Улыбка
        pygame.draw.arc(surf, WHITE, (10, 25, 20, 15), 0, 3.14, 2)
        run_frames.append(surf)

    animations["run"] = Animation(run_frames, speed=0.2)

    # Анимация прыжка
    jump_frames = []
    for i in range(3):
        surf = pygame.Surface((40, 60), pygame.SRCALPHA)
        surf.fill(BLUE)

        # Поджатые ноги
        pygame.draw.rect(surf, (80, 120, 200), (15, 50, 10, 10))

        # Взволнованные глаза
        eye_size = 6 if i == 1 else 5
        pygame.draw.circle(surf, WHITE, (10, 15), eye_size)
        pygame.draw.circle(surf, WHITE, (30, 15), eye_size)
        pygame.draw.circle(surf, BLACK, (10, 15), 3)
        pygame.draw.circle(surf, BLACK, (30, 15), 3)

        # Открытый рот
        pygame.draw.ellipse(surf, WHITE, (12, 30, 16, 8))
        jump_frames.append(surf)

    animations["jump"] = Animation(jump_frames, speed=0.15, loop=False)

    return animations


def create_coin_animations():
    """Анимации монеток"""
    animations = {}

    # Вращение монетки
    spin_frames = []
    for angle in range(0, 360, 45):
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)

        # Эллипс, вращающийся вокруг своей оси
        rotated_coin = pygame.Surface((20, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(rotated_coin, (255, 215, 0), (0, 0, 20, 12))
        pygame.draw.ellipse(rotated_coin, (255, 255, 200), (4, 2, 12, 8))

        # Поворот
        rotated = pygame.transform.rotate(rotated_coin, angle)
        rect = rotated.get_rect(center=(12, 12))
        surf.blit(rotated, rect)

        # Ободок
        pygame.draw.circle(surf, (150, 100, 0), (12, 12), 10, 2)

        spin_frames.append(surf)

    animations["spin"] = Animation(spin_frames, speed=0.3)

    # Мерцание
    glow_frames = []
    for i in range(5):
        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        glow_size = 10 + i
        pygame.draw.circle(surf, (255, 255, 150, 100),
                           (12, 12), glow_size)
        pygame.draw.circle(surf, (255, 215, 0), (12, 12), 8)
        pygame.draw.circle(surf, (255, 255, 200), (12, 12), 5)
        glow_frames.append(surf)

    animations["glow"] = Animation(glow_frames, speed=0.2)

    return animations