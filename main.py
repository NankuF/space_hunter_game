import random
import time
import asyncio
import curses

from animations.animate_spaceship import animate_spaceship

with open('animations/rocket_frame_1.txt') as file:
    rocket_frame_1 = file.read()

with open('animations/rocket_frame_2.txt') as file:
    rocket_frame_2 = file.read()


class EventLoopCommand():

    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):

    def __init__(self, seconds):
        self.seconds = seconds


def draw(canvas):
    canvas.border()
    # Получаем размер окна (высота,ширина)
    window_height, window_width = curses.window.getmaxyx(canvas)
    # Создаем корутины
    coroutines = []
    stars_counter = 100
    indent = 3
    for index in range(stars_counter):
        star_shape = random.choice(['*', ':', '.', '+'])
        star_height = random.randint(indent, window_height - indent)
        star_width = random.randint(indent, window_width - indent)
        coroutines.append(blink(canvas, row=star_height, column=star_width, symbol=star_shape))

    fire_coros = []
    fire_coro = fire(canvas, start_row=window_height // 2, start_column=window_width // 2)
    fire_coros.append(fire_coro)
    ship_animation = animate_spaceship(canvas,
                                       rocket_frame_1, rocket_frame_2,
                                       start_row=window_height // 2, start_column=window_width // 2,
                                       eventloop=Sleep, sleep=1)

    while True:
        # Запускаем корутины
        for coroutine in coroutines:
            sleep_command = coroutine.send(None)
            canvas.refresh()
        for index in range(stars_counter // 2):
            coroutines[random.randint(0, len(coroutines) - 1)].send(None)
            canvas.refresh()
        # fire
        for coro in fire_coros.copy():
            try:
                coro.send(None)
            except StopIteration:
                fire_coros.remove(coro)
        # ship animations
        ship_animation.send(None)
        canvas.refresh()
        ship_animation.send(None)
        # Кудато сюда надо прикрутить read_controls(),чтобы корабль двигался. неясно как, тк
        # read_controls() блокирует работу асинхронного кода.

        time.sleep(sleep_command.seconds)


async def blink(canvas, row, column, symbol='*'):
    brightness = [curses.A_DIM, curses.A_NORMAL, curses.A_BOLD, curses.A_NORMAL]
    pause = [2, 0.3, 0.5, 0.3]
    while True:
        for index in range(4):
            canvas.addstr(row, column, symbol, brightness[index])
            await Sleep(pause[index])


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)
