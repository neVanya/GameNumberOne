"""
main.py - Главный файл игры
"""
import pygame
import sys

# Настройки экрана (добавляем здесь)
WIDTH, HEIGHT = 800, 600

def main():
    # Инициализация Pygame
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.font.init()

    print("Pygame инициализирован")

    # Создаем экран
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Мой Платформер")

    # Инициализируем аудио
    from audio import audio_manager
    audio_manager.initialize()

    # Простое меню
    menu_result = run_simple_menu(screen)

    if menu_result == "play":
        # Запускаем игру
        from game import Game
        game = Game(start_level=1)
        game.run()
    elif menu_result == "exit":
        pygame.quit()
        sys.exit()

def run_simple_menu(screen):
    """Простое меню без сложной логики"""
    from fonts import render_text

    # Цвета
    WHITE = (255, 255, 255)
    BLUE = (100, 149, 237)
    BLACK = (20, 20, 20)

    # Кнопки
    buttons = [
        {"text": "ИГРАТЬ", "rect": pygame.Rect(300, 200, 200, 50), "action": "play"},
        {"text": "ВЫХОД", "rect": pygame.Rect(300, 270, 200, 50), "action": "exit"},
    ]

    clock = pygame.time.Clock()

    # Запускаем музыку
    from audio import audio_manager
    audio_manager.play_music()

    while True:
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

        # Отрисовка
        screen.fill((0, 0, 30))

        # Заголовок
        title = render_text("ПЛАТФОРМЕР", size="title", color=BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Кнопки
        for button in buttons:
            # Проверка наведения
            hover = button["rect"].collidepoint(mouse_pos)
            color = (70, 130, 180) if hover else BLUE

            # Рисуем кнопку
            pygame.draw.rect(screen, color, button["rect"], border_radius=10)
            pygame.draw.rect(screen, WHITE, button["rect"], 3, border_radius=10)

            # Текст кнопки
            text = render_text(button["text"], size="medium", color=WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            screen.blit(text, text_rect)

            # Нажатие
            if hover and mouse_click:
                return button["action"]

        # Инструкция
        inst = render_text("Нажми Enter для начала игры или ESC для выхода",
                          size="small", color=WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()