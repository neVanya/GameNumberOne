"""
fonts.py - Простая система шрифтов
"""
import pygame


def render_text(text, size="medium", color=(255, 255, 255)):
    """Рендеринг текста"""
    # Выбираем размер шрифта
    if size == "small":
        font_size = 20
    elif size == "medium":
        font_size = 28
    elif size == "large":
        font_size = 36
    elif size == "title":
        font_size = 48
    else:
        font_size = 28

    # Создаем шрифт
    try:
        font = pygame.font.Font(None, font_size)
    except:
        font = pygame.font.SysFont("arial", font_size)

    # Рендерим текст
    return font.render(text, True, color)