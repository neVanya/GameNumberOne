import sys
import random
from settings import *
from fonts import render_text
import pygame


class Button:
    """Кнопка меню"""

    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=(70, 130, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)

        # Используем нашу функцию рендеринга
        text_surf = render_text(self.text, size="medium", color=WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click


class MainMenu:
    """Главное меню"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = False

        # Кнопки
        button_width = 200
        button_height = 50
        center_x = WIDTH // 2 - button_width // 2

        self.buttons = [
            Button(center_x, 200, button_width, button_height, "ИГРАТЬ"),
            Button(center_x, 270, button_width, button_height, "УРОВНИ"),
            Button(center_x, 340, button_width, button_height, "НАСТРОЙКИ"),
            Button(center_x, 410, button_width, button_height, "ВЫХОД"),
        ]

        # Фон
        self.bg_offset = 0

        # Анимация частиц для фона
        self.particles = []
        self.create_background_particles()

    def create_background_particles(self):
        """Создание частиц для фона меню"""
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5),
                'color': random.choice([BLUE, GREEN, (255, 215, 0)])
            })

    def update_background(self):
        """Обновление фона с частицами"""
        for p in self.particles:
            p['y'] += p['speed']
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)

    def draw_background(self):
        """Отрисовка фона"""
        # Градиент
        for y in range(HEIGHT):
            color_value = int(10 + (y / HEIGHT) * 50)
            color = (color_value, color_value, color_value + 50)
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        # Частицы
        for p in self.particles:
            pygame.draw.circle(self.screen, p['color'],
                               (int(p['x']), int(p['y'])), p['size'])

    def draw(self):
        """Отрисовка меню"""
        self.screen.fill((0, 0, 0))
        self.draw_background()

        # Заголовок с тенью
        title_text = render_text("ПЛАТФОРМЕР", size="title", color=BLUE)
        shadow_text = render_text("ПЛАТФОРМЕР", size="title", color=BLACK)

        shadow_offset = 5
        self.screen.blit(shadow_text,
                         (WIDTH // 2 - shadow_text.get_width() // 2 + shadow_offset,
                          100 + shadow_offset))
        self.screen.blit(title_text,
                         (WIDTH // 2 - title_text.get_width() // 2, 100))

        # Кнопки
        for button in self.buttons:
            button.draw(self.screen)

        # Инструкция
        inst_text = render_text("Используйте мышь для выбора меню",
                                size="small", color=WHITE)
        self.screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

    def run(self):
        """Запуск меню"""
        self.running = True

        # Запускаем музыку (если не играет)
        from audio import audio_manager
        if not audio_manager.music_playing:
            audio_manager.play_music()

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "exit"
                    if event.key == pygame.K_RETURN:
                        return "play"

            # Проверка кнопок
            for i, button in enumerate(self.buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    if i == 0:  # Играть
                        return "play"
                    elif i == 1:  # Уровни
                        return "levels"
                    elif i == 2:  # Настройки
                        return "settings"
                    elif i == 3:  # Выход
                        return "exit"

            # Обновление фона
            self.update_background()
            self.draw()
            self.clock.tick(60)

        return "exit"


class LevelSelectMenu:
    """Меню выбора уровня"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Кнопки уровней
        self.level_buttons = []
        button_size = 80
        margin = 20

        for i in range(3):  # 3 уровня
            x = WIDTH // 2 - button_size // 2
            y = 150 + i * (button_size + margin)
            button = Button(x, y, button_size, button_size, "")
            self.level_buttons.append(button)

        # Кнопка возврата
        self.back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, "НАЗАД")

        # Загрузка прогресса
        self.unlocked_levels = self.load_progress()

        # Названия уровней
        self.level_names = ["Начальный уровень", "Лесная зона", "Опасная территория"]

    def load_progress(self):
        """Загрузка прогресса из файла"""
        try:
            with open("progress.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 1

    def draw(self):
        """Отрисовка меню выбора уровня"""
        self.screen.fill((0, 0, 30))

        # Заголовок
        title_text = render_text("ВЫБОР УРОВНЯ", size="title", color=BLUE)
        self.screen.blit(title_text,
                         (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Кнопки уровней
        for i, button in enumerate(self.level_buttons):
            level_num = i + 1

            # Проверка доступности уровня
            if level_num <= self.unlocked_levels:
                button.color = GREEN
                button.hover_color = (50, 200, 50)
            else:
                button.color = (100, 100, 100)
                button.hover_color = (80, 80, 80)

            button.draw(self.screen)

            # Номер уровня или замок
            if level_num <= self.unlocked_levels:
                level_text = render_text(str(level_num), size="large", color=WHITE)
            else:
                level_text = render_text("🔒", size="large", color=WHITE)

            level_rect = level_text.get_rect(center=button.rect.center)
            self.screen.blit(level_text, level_rect)

            # Название уровня
            if level_num <= self.unlocked_levels:
                name_text = render_text(self.level_names[i], size="small", color=WHITE)
                self.screen.blit(name_text,
                                 (button.rect.centerx - name_text.get_width() // 2,
                                  button.rect.bottom + 10))

        # Кнопка возврата
        self.back_button.draw(self.screen)

        # Прогресс
        if self.unlocked_levels < 3:
            progress_text = render_text(f"Открыто уровней: {self.unlocked_levels}/3",
                                        size="small", color=WHITE)
            self.screen.blit(progress_text,
                             (WIDTH // 2 - progress_text.get_width() // 2, HEIGHT - 150))

        pygame.display.flip()

    def run(self):
        """Запуск меню выбора уровня"""
        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

            # Проверка кнопок уровней
            for i, button in enumerate(self.level_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    level_num = i + 1
                    if level_num <= self.unlocked_levels:
                        return level_num

            # Проверка кнопки возврата
            self.back_button.check_hover(mouse_pos)
            if self.back_button.is_clicked(mouse_pos, mouse_click):
                return None

            self.draw()
            self.clock.tick(60)


class SettingsMenu:
    """Меню настроек"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Настройки
        self.volume = 0.7
        self.show_fps = True

        # Слайдер громкости
        self.volume_slider = {
            'rect': pygame.Rect(WIDTH // 2 - 150, 200, 300, 20),
            'handle_pos': self.volume * 300,
            'dragging': False
        }

        # Чекбокс FPS
        self.fps_checkbox = {
            'rect': pygame.Rect(WIDTH // 2 - 150, 280, 30, 30),
            'checked': self.show_fps
        }

        # Кнопки
        self.apply_button = Button(WIDTH // 2 - 100, 350, 200, 50, "ПРИМЕНИТЬ", GREEN)
        self.back_button = Button(WIDTH // 2 - 100, 420, 200, 50, "НАЗАД")

    def draw(self):
        """Отрисовка меню настроек"""
        self.screen.fill((0, 0, 30))

        # Заголовок
        title_text = render_text("НАСТРОЙКИ", size="title", color=BLUE)
        self.screen.blit(title_text,
                         (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Громкость
        volume_label = render_text("Громкость:        ", size="medium", color=WHITE)
        self.screen.blit(volume_label, (WIDTH // 2 - 200, 195))

        # Слайдер громкости
        pygame.draw.rect(self.screen, (100, 100, 100), self.volume_slider['rect'])
        pygame.draw.rect(self.screen, BLUE,
                         (self.volume_slider['rect'].x,
                          self.volume_slider['rect'].y,
                          self.volume_slider['handle_pos'],
                          self.volume_slider['rect'].height))

        # Ползунок слайдера
        handle_rect = pygame.Rect(
            self.volume_slider['rect'].x + self.volume_slider['handle_pos'] - 10,
            self.volume_slider['rect'].y - 5,
            20, 30
        )
        pygame.draw.rect(self.screen, WHITE, handle_rect, border_radius=5)

        # Процент громкости
        percent = int(self.volume * 100)
        percent_text = render_text(f"{percent}%", size="medium", color=WHITE)
        self.screen.blit(percent_text,
                         (self.volume_slider['rect'].right + 20,
                          self.volume_slider['rect'].centery - percent_text.get_height() // 2))

        # Показ FPS
        fps_label = render_text("Показывать FPS:           ", size="medium", color=WHITE)
        self.screen.blit(fps_label, (WIDTH // 2 - 200, 275))

        # Чекбокс
        pygame.draw.rect(self.screen, WHITE, self.fps_checkbox['rect'], 2)
        if self.fps_checkbox['checked']:
            check_rect = pygame.Rect(
                self.fps_checkbox['rect'].x + 5,
                self.fps_checkbox['rect'].y + 5,
                self.fps_checkbox['rect'].width - 10,
                self.fps_checkbox['rect'].height - 10
            )
            pygame.draw.rect(self.screen, GREEN, check_rect)

        # Кнопки
        self.apply_button.draw(self.screen)
        self.back_button.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """Запуск меню настроек"""
        from audio import audio_manager
        if not audio_manager.music_playing:
            audio_manager.play_music()

        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            mouse_down = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                        mouse_down = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.volume_slider['dragging'] = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False

            # Обработка слайдера
            if mouse_down and self.volume_slider['rect'].collidepoint(mouse_pos):
                self.volume_slider['dragging'] = True

            if self.volume_slider['dragging']:
                rel_x = mouse_pos[0] - self.volume_slider['rect'].x
                self.volume_slider['handle_pos'] = max(0, min(300, rel_x))
                self.volume = self.volume_slider['handle_pos'] / 300
                audio_manager.set_volume(self.volume)

            # Обработка чекбокса
            if mouse_click and self.fps_checkbox['rect'].collidepoint(mouse_pos):
                self.fps_checkbox['checked'] = not self.fps_checkbox['checked']

            # Обработка кнопок
            self.apply_button.check_hover(mouse_pos)
            self.back_button.check_hover(mouse_pos)

            if self.apply_button.is_clicked(mouse_pos, mouse_click):
                self.save_settings()
                return True

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                return False

            self.draw()
            self.clock.tick(60)

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open("settings.txt", "w") as f:
                f.write(f"volume={self.volume}\n")
                f.write(f"show_fps={int(self.fps_checkbox['checked'])}")
        except:
            pass

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            with open("settings.txt", "r") as f:
                for line in f:
                    if line.startswith("volume="):
                        self.volume = float(line.split("=")[1])
                        self.volume_slider['handle_pos'] = self.volume * 300
                    elif line.startswith("show_fps="):
                        self.show_fps = bool(int(line.split("=")[1]))
                        self.fps_checkbox['checked'] = self.show_fps
        except:
            pass