from random import randint

import pygame as pg

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цветовая палитра игры
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # цвет фона — чёрный
BORDER_COLOR = (93, 216, 228)       # цвет границы ячейки
APPLE_COLOR = (255, 0, 0)           # цвет яблока
SNAKE_COLOR = (0, 255, 0)           # цвет змейки

# Скорость движения змейки
SPEED = 20

# Настройка игрового окна
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()

# Словарь допустимых поворотов
DIRECTION_MAP = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}


class GameObject:
    """Базовый класс для всех игровых объектов.

    Предоставляет общие атрибуты (позиция, цвет) и методы отрисовки
    для наследников — Apple и Snake.
    """

    def __init__(self, position=CENTER_POSITION, body_color=BOARD_BACKGROUND_COLOR):
        """Инициализирует объект с заданной позицией и цветом."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну ячейку на игровом поле."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        fill_color = color if color is not None else self.body_color
        pg.draw.rect(screen, fill_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект в его текущей позиции."""
        self.draw_cell(self.position)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, snake_positions=None):
        """Создаёт яблоко в случайной позиции."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(snake_positions or [CENTER_POSITION])

    def randomize_position(self, snake_positions):
        """Задаёт яблоку новую случайную позицию, не занятую змейкой."""
        while self.position in snake_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Создаёт змейку в центре поля."""
        super().__init__(position=CENTER_POSITION, body_color=SNAKE_COLOR)
        self.positions = [CENTER_POSITION]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применяет отложенное направление, если оно задано."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну ячейку в текущем направлении.

        Голова добавляется в начало списка. Если длина не выросла, 
        последний сегмент удаляется. Проходит сквозь границы. 
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions[-1]
            self.positions.pop()
        else:
            self.last = None

    def grow(self):
        """Увеличивает длину змейки (при поедании яблока)."""
        self.length += 1

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [CENTER_POSITION]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self):
        """Отрисовывает голову змейки и затирает след хвоста."""
        self.draw_cell(self.positions[0])
        if self.last:
            rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и задаёт следующее направление."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            game_object.next_direction = DIRECTION_MAP.get(
                (game_object.direction, event.key), game_object.direction
            )


def main():
    """Инициализация pygame, основной игровой цикл и логика игры."""
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        elif snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
