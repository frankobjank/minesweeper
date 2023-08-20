import random
import time
from pyray import *

# for incorporating medium and hard, start with menu to choose difficulty
# then use set_window_size based on selection

# globals
MOUSE_BUTTON_LEFT= 0
MOUSE_BUTTON_RIGHT= 1
MOUSE_BUTTON_MIDDLE= 2

block = 30
header_height=block*2
screen_width=block*10
screen_height=block*10+header_height
num_mines = 10
reset_button = Vector2(screen_width//2-block*2, block//2)

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.adj = 0 # adj to mines number
        self.mine = False
        self.flag = False
        self.visible = False

class State:
    def __init__(self):
        self.board = {}
        self.mines = set()
        self.selection = None
        self.visible_squares = set()


def create_board(state, num_mines, fixed_mines=False):
    state.board = {(x, y): Square(x, y) for y in range(header_height, screen_height, block) for x in range(0, screen_width, block)}
    # fixed_mines mines for debugging
    if fixed_mines == True:
        state.mines = [(8, 0), (48, 0), (16, 8), (0, 24), (56, 24), (24, 32), (72, 32), (0, 40), (16, 40), (16, 56)]
        for mine in state.mines:
            state.board[(mine)].mine = True
    # random mines
    else:
        # mines = set() # local set to get up to 10 and exclude dupes
        while len(state.mines)<num_mines:
            mine = (get_random_value(0, screen_width), get_random_value(0, screen_height))
            # mines.add(mine)
            state.mines.add(state.board[(mine)]) # global mines
            state.board[(mine)].mine = True
    
    # calc adj to mines
    for mine in state.mines:
        # print((mine.x, mine.y)) # for debugging
        all_adjacent = mine.get_adjacent(state, exclude="mine")
        for adj in all_adjacent:
            adj.adj += 1


def update(state):
    if is_mouse_button_down(0):
        state.selection = get_mouse_position()
        state.selection.x -= state.selection.x % 30
        state.selection.y -= state.selection.y % 30
        state.selection = state.board.get((state.selection.x, state.selection.y), None)

    elif is_mouse_button_released(0):
        if state.selection:
            state.selection.visible = True
            state.visible_squares.add(state.selection)
            state.selection = None

def render(state):
    begin_drawing()
    clear_background(LIGHTGRAY)
    for square in state.board.values():
        draw_rectangle(square.x, square.y, 30, 30, DARKGRAY)
    if state.selection:
        draw_rectangle(state.selection.x, state.selection.y, 30, 30, LIGHTGRAY)

    for square in state.visible_squares:
        draw_rectangle(square.x, square.y, 30, 30, RED)

    for x in range(0, screen_width, block):
        draw_line(x, header_height, x, screen_height, BLACK)
    for y in range(header_height, screen_height, block):
        draw_line(0, y, screen_width, y, BLACK)
    draw_rectangle_v(state.start_button, state.start_button, GRAY)
    end_drawing()

state = State()
def main(state):
    set_target_fps(60)
    init_window(screen_width, screen_height, "Minesweeper")
    while not window_should_close():
        update(state)
        render(state)

    close_window()

main(state)