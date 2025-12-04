import pygame
import sys
from settings import *
from player import Player
from platform import Platform
from coin import Coin
from enemy import Enemy
from levels import get_level_data, get_background_color


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Моя игра - Уровень 1")
        self.clock = pygame.time.Clock()

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Текущий уровень
        self.current_level = 1
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
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def create_level(self):
        """Создание уровня из данных"""
        # Очищаем предыдущий уровень
        self.all_sprites.empty()
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()

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

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_r:
                    self.restart_level()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_n:
                    self.next_level()  # Тестовая кнопка для перехода на след. уровень

        # Непрерывное движение
        keys = pygame.key.get_pressed()
        self.player.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

    def update(self):
        """Обновление игры"""
        # Обновление всех спрайтов
        self.all_sprites.update()

        # Передаем игрока врагам для ИИ
        for enemy in self.enemies:
            enemy.update(self.player)

        # Обработка столкновений игрока с платформами
        self.player.handle_collisions(self.platforms)

        # Проверка сбора монет
        collected_coins = pygame.sprite.spritecollide(
            self.player, self.coins, False)

        for coin in collected_coins:
            if not coin.collected:
                coin.collect()
                self.score += coin.value

        # Проверка столкновения с врагами
        hit_enemies = pygame.sprite.spritecollide(
            self.player, self.enemies, False)

        for enemy in hit_enemies:
            # Проверяем, если игрок прыгнул на врага сверху
            if (self.player.vel_y > 0 and
                    self.player.rect.bottom <= enemy.rect.centery + 20):
                # Убиваем врага
                if enemy.take_damage():
                    self.score += 50  # Бонус за убийство врага
            else:
                # Игрок получает урон
                self.player_lives -= 1
                # Отбрасывание игрока
                self.player.vel_y = -10
                self.player.rect.x -= 50 * (1 if enemy.rect.x < self.player.rect.x else -1)

                if self.player_lives <= 0:
                    self.game_over()

        # Проверка столкновения с пулями (для стреляющих врагов)
        for enemy in self.enemies:
            if enemy.enemy_type == "shooter":
                hit_bullets = pygame.sprite.spritecollide(
                    self.player, enemy.bullets, True)
                if hit_bullets:
                    self.player_lives -= 1
                    self.player.vel_y = -10
                    if self.player_lives <= 0:
                        self.game_over()

        # Проверка завершения уровня
        if len(self.coins) == 0 and self.score >= self.level_data["required_score"]:
            self.level_complete()

    def draw(self):
        """Отрисовка игры"""
        # Фон
        bg_color = get_background_color(self.level_data["background"])
        self.screen.fill(bg_color)

        # Облака (только для небесного фона)
        if self.level_data["background"] == "sky":
            for i in range(3):
                x = (pygame.time.get_ticks() // 50 + i * 300) % (WIDTH + 200) - 100
                pygame.draw.circle(self.screen, WHITE, (x, 80), 30)
                pygame.draw.circle(self.screen, WHITE, (x + 25, 70), 25)
                pygame.draw.circle(self.screen, WHITE, (x - 25, 70), 25)

        # Все спрайты
        self.all_sprites.draw(self.screen)

        # Отрисовка пуль стреляющих врагов
        for enemy in self.enemies:
            if enemy.enemy_type == "shooter":
                enemy.draw_bullets(self.screen)

        # UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Отрисовка интерфейса"""
        # Счёт
        score_text = self.font.render(f"Очки: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Уровень
        level_text = self.font.render(f"Уровень: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))

        # Название уровня
        name_text = self.small_font.render(self.level_data["name"], True, WHITE)
        self.screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 10))

        # Требуемые очки
        req_text = self.small_font.render(
            f"Нужно очков: {self.level_data['required_score']}", True, WHITE)
        self.screen.blit(req_text, (WIDTH // 2 - req_text.get_width() // 2, 40))

        # Жизни
        self.draw_lives()

        # Инструкции
        controls = [
            "Управление:",
            "← → / A D - движение",
            "Пробел - прыжок",
            "R - рестарт уровня",
            "N - след. уровень (тест)",
            "ESC - выход"
        ]

        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(control_text, (WIDTH - 200, 10 + i * 25))

    def draw_lives(self):
        """Отрисовка количества жизней"""
        lives_text = self.font.render(f"Жизни: {self.player_lives}", True, WHITE)
        self.screen.blit(lives_text, (WIDTH - 200, HEIGHT - 50))

        # Визуализация сердечками
        for i in range(self.player_lives):
            x = WIDTH - 200 + i * 35
            y = HEIGHT - 90
            # Рисуем сердечко
            pygame.draw.circle(self.screen, RED, (x + 8, y + 8), 8)
            pygame.draw.circle(self.screen, RED, (x + 22, y + 8), 8)
            pygame.draw.polygon(self.screen, RED, [
                (x, y + 15),
                (x + 15, y + 25),
                (x + 30, y + 15)
            ])

    def level_complete(self):
        """Завершение уровня"""
        # Сохраняем прогресс
        self.save_progress()

        # Показываем экран завершения уровня
        complete_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)

        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Текст
        complete_text = complete_font.render("УРОВЕНЬ ПРОЙДЕН!", True, GREEN)
        self.screen.blit(complete_text,
                         (WIDTH // 2 - complete_text.get_width() // 2,
                          HEIGHT // 2 - 100))

        # Счёт
        score_text = score_font.render(f"Ваш счёт: {self.score}",
                                       True, WHITE)
        self.screen.blit(score_text,
                         (WIDTH // 2 - score_text.get_width() // 2,
                          HEIGHT // 2))

        # Инструкция
        next_text = score_font.render("Нажми N для след. уровня",
                                      True, WHITE)
        self.screen.blit(next_text,
                         (WIDTH // 2 - next_text.get_width() // 2,
                          HEIGHT // 2 + 80))

        pygame.display.flip()

        # Ожидание нажатия
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.next_level()
                        waiting = False
                    if event.key == pygame.K_r:
                        self.restart_level()
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def game_over(self):
        """Конец игры"""
        # Сохраняем рекорд
        self.save_high_score()

        # Показываем экран Game Over
        game_over_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)

        # Затемняем экран
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Текст Game Over
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text,
                         (WIDTH // 2 - game_over_text.get_width() // 2,
                          HEIGHT // 2 - 100))

        # Финальный счёт
        score_text = score_font.render(f"Финальный счёт: {self.score}",
                                       True, WHITE)
        self.screen.blit(score_text,
                         (WIDTH // 2 - score_text.get_width() // 2,
                          HEIGHT // 2))

        # Инструкция
        restart_text = score_font.render("Нажми R чтобы перезапустить",
                                         True, WHITE)
        self.screen.blit(restart_text,
                         (WIDTH // 2 - restart_text.get_width() // 2,
                          HEIGHT // 2 + 80))

        pygame.display.flip()

        # Ожидание нажатия R
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1
        if self.current_level > 3:  # У нас только 3 уровня
            self.current_level = 1

        # Обновляем данные уровня
        self.level_data = get_level_data(self.current_level)

        # Обновляем заголовок окна
        pygame.display.set_caption(f"Моя игра - Уровень {self.current_level}")

        # Пересоздаем уровень
        start_x, start_y = self.level_data["player_start"]
        self.player.rect.x = start_x
        self.player.rect.y = start_y
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.on_ground = False

        self.create_level()

    def restart_level(self):
        """Рестарт текущего уровня"""
        self.player_lives = 3
        self.score = 0

        start_x, start_y = self.level_data["player_start"]
        self.player.rect.x = start_x
        self.player.rect.y = start_y
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.on_ground = False

        self.create_level()

    def restart_game(self):
        """Полный рестарт игры"""
        self.current_level = 1
        self.score = 0
        self.player_lives = 3
        self.level_data = get_level_data(self.current_level)

        pygame.display.set_caption(f"Моя игра - Уровень {self.current_level}")

        start_x, start_y = self.level_data["player_start"]
        self.player.rect.x = start_x
        self.player.rect.y = start_y
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.on_ground = False

        self.create_level()

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
            with open("progress.txt", "w") as f:
                f.write(str(self.current_level))
        except:
            pass

    def run(self):
        """Главный игровой цикл"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)