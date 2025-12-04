import pygame
import sys
import random
import math

from fonts import render_text
from settings import *
from player import Player
from platform import Platform
from coin import Coin
from enemy import Enemy
from levels import get_level_data, get_background_color
from particles import (
    ParticleSystem, create_collect_effect, create_jump_effect,
    create_enemy_death_effect, create_hit_effect
)
from audio import audio_manager


class Game:
    def __init__(self, start_level=1):
        # ВСЁ уже инициализировано в main.py
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Мой Платформер - Уровень {start_level}")
        self.clock = pygame.time.Clock()

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Системы частиц
        self.particle_systems = []

        # Текущий уровень
        self.current_level = start_level
        self.level_data = get_level_data(self.current_level)

        # Создание игрока
        start_x, start_y = self.level_data["player_start"]
        self.player = Player(start_x, start_y)
        self.all_sprites.add(self.player)

        # Создание уровня
        self.create_level()

        # Игровые параметры
        self.score = 0
        self.player_lives = 3

        # Состояния игры
        self.game_paused = False
        self.game_over = False
        self.level_complete = False

        # Время и таймеры
        self.level_time = 0
        self.invincibility_timer = 0
        self.flash_timer = 0

        # Эффекты экрана
        self.screen_shake = 0
        self.flash_color = None
        self.flash_alpha = 0

        # Запускаем музыку (если не играет)
        if not audio_manager.music_playing:
            audio_manager.play_music()

    def create_level(self):
        """Создание уровня из данных"""
        # Очищаем предыдущий уровень
        self.all_sprites.empty()
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        self.particle_systems.clear()

        # Добавляем игрока
        self.all_sprites.add(self.player)

        # Создаем платформы
        for plat_data in self.level_data["platforms"]:
            platform = Platform(*plat_data)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

        # Создаем монетки
        for coin_data in self.level_data["coins"]:
            coin = Coin(*coin_data)
            self.all_sprites.add(coin)
            self.coins.add(coin)

        # Создаем врагов
        for enemy_data in self.level_data["enemies"]:
            enemy = Enemy(*enemy_data)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

        # Сброс состояния игрока
        start_x, start_y = self.level_data["player_start"]
        self.player.rect.x = start_x
        self.player.rect.y = start_y
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.on_ground = False

        # Сброс таймеров
        self.level_time = 0
        self.invincibility_timer = 0
        self.screen_shake = 0

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_paused and not self.game_over and not self.level_complete:
                        jump_effect = self.player.jump()
                        if jump_effect:
                            self.particle_systems.append(jump_effect)
                            audio_manager.play_sound("jump")

                if event.key == pygame.K_r:
                    self.restart_level()

                if event.key == pygame.K_ESCAPE:
                    self.game_paused = not self.game_paused

                if event.key == pygame.K_n and (self.game_over or self.level_complete):
                    if self.game_over:
                        self.restart_game()
                    else:
                        self.next_level()

                if event.key == pygame.K_p:
                    # Тестовая кнопка для эффектов
                    self.create_test_effect()

                if event.key == pygame.K_m:  # M - вернуться в меню
                    self.return_to_menu()

        # Непрерывное движение (только если игра не на паузе)
        if not self.game_paused and not self.game_over and not self.level_complete:
            keys = pygame.key.get_pressed()
            self.player.vel_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()

    def update(self):
        """Обновление игры"""
        if self.game_paused or self.game_over or self.level_complete:
            return

        # Увеличиваем время уровня
        self.level_time += 1

        # Обновление таймеров
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.flash_alpha = max(0, self.flash_alpha - 5)

        # Обновление эффекта тряски экрана
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - 1)

        # Обновление всех спрайтов
        self.all_sprites.update()

        # Передаем игрока врагам для ИИ
        for enemy in self.enemies:
            enemy.update(self.player)

        # Обновление систем частиц
        for particle_system in self.particle_systems[:]:
            particle_system.update()
            if not particle_system.particles:
                self.particle_systems.remove(particle_system)

        # Обработка столкновений игрока с платформами
        self.player.handle_collisions(self.platforms)

        # Проверка сбора монет
        collected_coins = pygame.sprite.spritecollide(
            self.player, self.coins, False)

        coins_to_remove = []
        for coin in collected_coins:
            if not coin.collected:
                collect_effect = coin.collect()
                if collect_effect:
                    self.particle_systems.append(collect_effect)
                    audio_manager.play_sound("coin")

                self.score += coin.value
                coins_to_remove.append(coin)

                # Маленькая тряска экрана при сборе монеты
                self.screen_shake = min(self.screen_shake + 2, 10)

        # Проверка столкновения с врагами (если не неуязвим)
        if self.invincibility_timer == 0:
            hit_enemies = pygame.sprite.spritecollide(
                self.player, self.enemies, False)

            for enemy in hit_enemies:
                # Проверяем, если игрок прыгнул на врага сверху
                if (self.player.vel_y > 0 and
                        self.player.rect.bottom <= enemy.rect.centery + 20):
                    # Убиваем врага
                    if enemy.take_damage():
                        self.score += 50
                        audio_manager.play_sound("enemy_death")

                        # Эффект смерти врага
                        death_effect = create_enemy_death_effect(
                            enemy.rect.centerx, enemy.rect.centery)
                        self.particle_systems.append(death_effect)

                        # Тряска экрана при убийстве врага
                        self.screen_shake = 15

                        # Отскок от врага
                        self.player.vel_y = -JUMP_POWER * 0.7
                else:
                    # Игрок получает урон
                    self.take_damage(enemy)

        # Проверка столкновения с пулями (для стреляющих врагов)
        for enemy in self.enemies:
            if enemy.enemy_type == "shooter":
                hit_bullets = pygame.sprite.spritecollide(
                    self.player, enemy.bullets, True)
                if hit_bullets and self.invincibility_timer == 0:
                    self.take_damage(None)

        # Проверка выпадения за экран
        if self.player.rect.top > HEIGHT + 100:
            self.take_damage(None, fall_damage=True)

        # Проверка завершения уровня
        if len(self.coins) == 0 and self.score >= self.level_data["required_score"]:
            self.complete_level()

    def take_damage(self, enemy=None, fall_damage=False):
        """Игрок получает урон"""
        self.player_lives -= 1
        audio_manager.play_sound("hurt")

        # Эффект получения урона
        hit_effect = create_hit_effect(
            self.player.rect.centerx, self.player.rect.centery)
        self.particle_systems.append(hit_effect)

        # Вспышка экрана
        self.flash_color = RED
        self.flash_alpha = 150
        self.flash_timer = 30

        # Тряска экрана
        self.screen_shake = 20

        # Неуязвимость после получения урона
        self.invincibility_timer = 90  # 1.5 секунды при 60 FPS

        if enemy and not fall_damage:
            # Отбрасывание от врага
            if enemy.rect.x < self.player.rect.x:
                # Враг слева - отбрасываем вправо
                self.player.rect.x += 30
                self.player.vel_x = 10
            else:
                # Враг справа - отбрасываем влево
                self.player.rect.x -= 30
                self.player.vel_x = -10

            # Отбрасывание вверх
            self.player.vel_y = -JUMP_POWER * 0.5

        if self.player_lives <= 0:
            self.game_over = True
            audio_manager.play_sound("hurt")
            self.save_high_score()

    def complete_level(self):
        """Завершение уровня"""
        self.level_complete = True
        audio_manager.play_sound("win")

        # Эффект завершения уровня
        for _ in range(5):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            effect = ParticleSystem()
            effect.emit_circle(x, y, count=20, color=GREEN, speed=3, lifetime=60)
            self.particle_systems.append(effect)

        # Сохраняем прогресс
        self.save_progress()

    def draw(self):
        """Отрисовка игры"""
        # Получаем цвет фона
        bg_color = get_background_color(self.level_data["background"])

        # Применяем тряску экрана
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        # Очищаем экран
        self.screen.fill(bg_color)

        # Облака (только для небесного фона) - рисуем ПЕРЕД UI
        if self.level_data["background"] == "sky":
            for i in range(3):
                x = (pygame.time.get_ticks() // 50 + i * 300) % (WIDTH + 200) - 100
                x += shake_x * 0.5

                # Рисуем облака на отдельной поверхности с прозрачностью
                cloud_surface = pygame.Surface((100, 60), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surface, (255, 255, 255, 180), (25, 30), 25)
                pygame.draw.circle(cloud_surface, (255, 255, 255, 180), (50, 20), 20)
                pygame.draw.circle(cloud_surface, (255, 255, 255, 180), (0, 20), 20)
                self.screen.blit(cloud_surface, (int(x) - 50, 50 + shake_y * 0.5))

        # Создаем поверхность для игрового мира (для применения тряски)
        game_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Отрисовка пуль стреляющих врагов
        for enemy in self.enemies:
            if enemy.enemy_type == "shooter":
                enemy.draw_bullets(game_surface)

        # Все спрайты на игровую поверхность
        self.all_sprites.draw(game_surface)

        # Частицы на игровую поверхность
        for particle_system in self.particle_systems:
            particle_system.draw(game_surface)

        # Применяем тряску к игровой поверхности
        self.screen.blit(game_surface, (shake_x, shake_y))

        # UI элементы (не трясутся) - рисуем ПОСЛЕ всего
        self.draw_ui()

        # Эффект вспышки
        if self.flash_alpha > 0 and self.flash_color:
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((*self.flash_color[:3], self.flash_alpha))
            self.screen.blit(flash_surface, (0, 0))

        # Эффект неуязвимости (мигание игрока)
        if self.invincibility_timer > 0:
            if (self.invincibility_timer // 3) % 2 == 0:
                # Создаем копию игрока с прозрачностью
                player_mask = pygame.mask.from_surface(self.player.image)
                player_outline = player_mask.to_surface(setcolor=WHITE, unsetcolor=None)
                player_outline.set_alpha(150)

                # Рисуем контур
                outline_pos = (self.player.rect.x + shake_x, self.player.rect.y + shake_y)
                self.screen.blit(player_outline, outline_pos)

        # Экран паузы
        if self.game_paused:
            self.draw_pause_screen()

        # Экран завершения уровня
        if self.level_complete:
            self.draw_level_complete_screen()

        # Экран Game Over
        if self.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_ui(self):
        """Отрисовка интерфейса"""
        # Счёт
        score_text = render_text(f"Очки: {self.score}", size="medium", color=WHITE)
        self.screen.blit(score_text, (10, 10))

        # Уровень
        level_text = render_text(f"Уровень: {self.current_level}", size="medium", color=WHITE)
        self.screen.blit(level_text, (10, 50))

        # Название уровня
        name_text = render_text(self.level_data["name"], size="small", color=WHITE)
        self.screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 10))

        # Требуемые очки
        req_text = render_text(f"Нужно очков: {self.level_data['required_score']}",
                               size="small", color=WHITE)
        self.screen.blit(req_text, (WIDTH // 2 - req_text.get_width() // 2, 40))

        # Оставшиеся монеты
        coins_left = len(self.coins)
        coins_text = render_text(f"Монеты: {coins_left}", size="small", color=WHITE)
        self.screen.blit(coins_text, (WIDTH // 2 - coins_text.get_width() // 2, 70))

        # Время уровня
        seconds = self.level_time // 60
        minutes = seconds // 60
        seconds = seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        time_text = render_text(f"Время: {time_str}", size="small", color=WHITE)
        self.screen.blit(time_text, (WIDTH - 150, 10))

        # Жизни - текст
        lives_text = render_text(f"Жизни:", size="medium", color=WHITE)
        self.screen.blit(lives_text, (WIDTH - 150, 50))

        # Визуализация сердечками
        for i in range(min(self.player_lives, 5)):  # Максимум 5 сердечек в строку
            x = WIDTH - 150 + 70 + i * 35
            y = 50

            # Рисуем сердечко
            # Левый круг
            pygame.draw.circle(self.screen, RED, (x + 8, y + 8), 8)
            # Правый круг
            pygame.draw.circle(self.screen, RED, (x + 22, y + 8), 8)
            # Треугольник снизу
            pygame.draw.polygon(self.screen, RED, [
                (x, y + 15),
                (x + 15, y + 25),
                (x + 30, y + 15)
            ])

            # Контур сердечка
            pygame.draw.circle(self.screen, (200, 0, 0), (x + 8, y + 8), 8, 1)
            pygame.draw.circle(self.screen, (200, 0, 0), (x + 22, y + 8), 8, 1)
            pygame.draw.polygon(self.screen, (200, 0, 0), [
                (x, y + 15),
                (x + 15, y + 25),
                (x + 30, y + 15)
            ], 1)

        # Если жизней больше 5, показываем число
        if self.player_lives > 5:
            extra_text = render_text(f"+{self.player_lives - 5}", size="small", color=RED)
            self.screen.blit(extra_text, (WIDTH - 150 + 70 + 5 * 35, 50))

        # Инструкции в правом нижнем углу
        controls = [
            "Управление:",
            "← → / A D - движение",
            "Пробел - прыжок",
            "ESC - пауза",
            "R - рестарт уровня",
            "M - в меню",
            "P - тест эффектов"
        ]

        y_offset = HEIGHT - 200
        for i, text in enumerate(controls):
            control_text = render_text(text, size="small", color=WHITE)
            self.screen.blit(control_text, (WIDTH - 220, y_offset + i * 25))

        # Индикатор неуязвимости (если активен)
        if self.invincibility_timer > 0:
            # Прогресс-бар неуязвимости
            bar_width = 100
            bar_height = 10
            bar_x = WIDTH - 150
            bar_y = 90

            # Фон прогресс-бара
            pygame.draw.rect(self.screen, (100, 100, 100),
                             (bar_x, bar_y, bar_width, bar_height))

            # Заполнение прогресс-бара
            progress = self.invincibility_timer / 90.0  # 90 кадров = 1.5 секунды
            fill_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, (255, 255, 0),
                             (bar_x, bar_y, fill_width, bar_height))

            # Текст "Неуязвимость"
            inv_text = render_text("Неуязвимость", size="small", color=(255, 255, 0))
            self.screen.blit(inv_text, (bar_x, bar_y - 20))

        # FPS счетчик (если включен в настройках)
        try:
            with open("settings.txt", "r") as f:
                for line in f:
                    if line.startswith("show_fps="):
                        if line.split("=")[1].strip() == "1":
                            fps_text = render_text(f"FPS: {int(self.clock.get_fps())}",
                                                   size="small", color=(200, 200, 200))
                            self.screen.blit(fps_text, (10, HEIGHT - 30))
                        break
        except:
            pass

    def draw_pause_screen(self):
        """Экран паузы"""
        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Текст PAUSE
        pause_text = render_text("ПАУЗА", size="title", color=BLUE)
        self.screen.blit(pause_text,
                         (WIDTH // 2 - pause_text.get_width() // 2,
                          HEIGHT // 2 - 100))

        # Инструкции
        inst1 = render_text("Нажми ESC для продолжения", size="medium", color=WHITE)
        inst2 = render_text("Нажми R для рестарта уровня", size="medium", color=WHITE)
        inst3 = render_text("Нажми M для выхода в меню", size="medium", color=WHITE)

        self.screen.blit(inst1, (WIDTH // 2 - inst1.get_width() // 2, HEIGHT // 2))
        self.screen.blit(inst2, (WIDTH // 2 - inst2.get_width() // 2, HEIGHT // 2 + 50))
        self.screen.blit(inst3, (WIDTH // 2 - inst3.get_width() // 2, HEIGHT // 2 + 100))

    def draw_level_complete_screen(self):
        """Экран завершения уровня"""
        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Текст
        complete_text = render_text("УРОВЕНЬ ПРОЙДЕН!", size="title", color=GREEN)
        self.screen.blit(complete_text,
                         (WIDTH // 2 - complete_text.get_width() // 2,
                          HEIGHT // 2 - 150))

        # Статистика
        seconds = self.level_time // 60
        minutes = seconds // 60
        seconds = seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        score_text = render_text(f"Счёт: {self.score}", size="large", color=WHITE)
        time_text = render_text(f"Время: {time_str}", size="large", color=WHITE)
        lives_text = render_text(f"Осталось жизней: {self.player_lives}", size="large", color=WHITE)

        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
        self.screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2))
        self.screen.blit(lives_text, (WIDTH // 2 - lives_text.get_width() // 2, HEIGHT // 2 + 50))

        # Инструкция
        next_text = render_text("Нажми N для след. уровня, R для рестарта или M для меню",
                                size="medium", color=WHITE)
        self.screen.blit(next_text,
                         (WIDTH // 2 - next_text.get_width() // 2,
                          HEIGHT // 2 + 120))

    def draw_game_over_screen(self):
        """Экран Game Over"""
        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Текст Game Over
        game_over_text = render_text("GAME OVER", size="title", color=RED)
        self.screen.blit(game_over_text,
                         (WIDTH // 2 - game_over_text.get_width() // 2,
                          HEIGHT // 2 - 150))

        # Статистика
        score_text = render_text(f"Финальный счёт: {self.score}", size="large", color=WHITE)
        level_text = render_text(f"Достигнут уровень: {self.current_level}", size="large", color=WHITE)

        # Загружаем рекорд
        try:
            with open("highscore.txt", "r") as f:
                high_score = int(f.read())
        except:
            high_score = 0

        high_text = render_text(f"Рекорд: {high_score}", size="large", color=(255, 215, 0))

        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 50))
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
        self.screen.blit(high_text, (WIDTH // 2 - high_text.get_width() // 2, HEIGHT // 2 + 50))

        # Новый рекорд?
        if self.score > high_score:
            new_record = render_text("НОВЫЙ РЕКОРД!", size="large", color=GREEN)
            self.screen.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, HEIGHT // 2 + 100))

        # Инструкция
        restart_text = render_text("Нажми N для новой игры, R для рестарта уровня или M для меню",
                                   size="medium", color=WHITE)
        self.screen.blit(restart_text,
                         (WIDTH // 2 - restart_text.get_width() // 2,
                          HEIGHT // 2 + 180))

    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1
        if self.current_level > 3:  # У нас только 3 уровня
            self.current_level = 1

        # Обновляем данные уровня
        self.level_data = get_level_data(self.current_level)

        # Обновляем заголовок окна
        pygame.display.set_caption(f"Мой Платформер - Уровень {self.current_level}")

        # Сброс состояния
        self.level_complete = False
        self.game_over = False
        self.score = 0
        self.player_lives = 3

        # Пересоздаем уровень
        self.create_level()

        # Звук начала уровня
        audio_manager.play_sound("jump")

    def restart_level(self):
        """Рестарт текущего уровня"""
        # Сброс состояния
        self.level_complete = False
        self.game_over = False
        self.game_paused = False
        self.score = 0
        self.player_lives = 3

        # Пересоздаем уровень
        self.create_level()

        # Звук рестарта
        audio_manager.play_sound("jump")

    def restart_game(self):
        """Полный рестарт игры"""
        self.current_level = 1
        self.score = 0
        self.player_lives = 3
        self.level_complete = False
        self.game_over = False
        self.game_paused = False
        self.level_data = get_level_data(self.current_level)

        pygame.display.set_caption(f"Мой Платформер - Уровень {self.current_level}")

        # Пересоздаем уровень
        self.create_level()

        # Звук начала игры
        audio_manager.play_sound("win")

    def return_to_menu(self):
        """Возврат в главное меню"""
        audio_manager.stop_music()
        self.quit_game()

    def save_high_score(self):
        """Сохранение рекорда в файл"""
        try:
            with open("highscore.txt", "r") as f:
                high_score = int(f.read())
        except:
            high_score = 0

        if self.score > high_score:
            with open("highscore.txt", "w") as f:
                f.write(str(self.score))

    def save_progress(self):
        """Сохранение прогресса"""
        try:
            # Сохраняем только если прошли уровень
            if self.current_level >= self.unlocked_levels:
                self.unlocked_levels = self.current_level + 1
                with open("progress.txt", "w") as f:
                    f.write(str(min(self.unlocked_levels, 3)))
        except:
            pass

    @property
    def unlocked_levels(self):
        """Получение количества открытых уровней"""
        try:
            with open("progress.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 1

    @unlocked_levels.setter
    def unlocked_levels(self, value):
        """Установка количества открытых уровней"""
        try:
            with open("progress.txt", "w") as f:
                f.write(str(min(value, 3)))
        except:
            pass

    def create_test_effect(self):
        """Тестовый эффект (для отладки)"""
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)

        effect = ParticleSystem()
        effect.emit_circle(x, y, count=30,
                           color=random.choice([BLUE, GREEN, RED, (255, 215, 0)]),
                           speed=random.uniform(2, 5),
                           lifetime=random.randint(40, 80))
        self.particle_systems.append(effect)

    def quit_game(self):
        """Выход из игры"""
        audio_manager.stop_music()
        pygame.quit()
        sys.exit()

    def run(self):
        """Главный игровой цикл"""
        running = True
        while running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)