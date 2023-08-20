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
        self.visible_squares = set()
        self.flags = set()
        self.selection = None


def create_board(state, num_mines, fixed_mines=False):
    state.board = {(x, y): Square(x, y) for y in range(header_height, screen_height, block) for x in range(0, screen_width, block)}
    # fixed_mines mines for debugging
    if fixed_mines == True:
        state.mines = [(30, 60), (180, 60), (60, 90), (0, 150), (210, 150), (90, 180), (270, 180), (0, 210), (60, 210), (60, 270)]
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
    
    # # calc adj to mines
    # for mine in state.mines:
    #     # print((mine.x, mine.y)) # for debugging
    #     all_adjacent = mine.get_adjacent(state, exclude="mine")
    #     for adj in all_adjacent:
    #         adj.adj += 1


def update(state):

    if is_mouse_button_down(0) or is_mouse_button_down(1):
        state.selection = get_mouse_position()
        state.selection.x -= state.selection.x % 30
        state.selection.y -= state.selection.y % 30
        state.selection = state.board.get((state.selection.x, state.selection.y), None)
        if state.selection.visible == True or state.selection.flag == True:
            state.selection = None  

    elif is_mouse_button_released(0):
        if state.selection:
            state.selection.visible = True
            state.visible_squares.add(state.selection)
            state.selection = None

    elif is_mouse_button_released(1):
        if state.selection != None and state.selection.visible == False:
            if state.selection.flag == False:
                state.selection.flag = True
                state.flags.add(state.selection)
                state.selection = None
            else:
                state.selection.flag = False
                state.flags.remove(state.selection)
                state.selection = None



def render(state):
    begin_drawing()
    clear_background(LIGHTGRAY)
    for square in state.board.values():
        if square == state.selection:
            draw_rectangle(state.selection.x, state.selection.y, 30, 30, LIGHTGRAY)
        elif square.flag == True:
            draw_rectangle(square.x, square.y, 30, 30, BLUE)
        elif square.visible == True:
            if square.mine == True:
                draw_rectangle(square.x, square.y, 30, 30, RED)
            else:
                draw_rectangle(square.x, square.y, 30, 30, GREEN)
        else:
            draw_rectangle(square.x, square.y, 30, 30, DARKGRAY)

    for x in range(0, screen_width, block):
        draw_line(x, header_height, x, screen_height, BLACK)
    for y in range(header_height, screen_height, block):
        draw_line(0, y, screen_width, y, BLACK)
    draw_rectangle_v(reset_button, reset_button, GRAY)
    end_drawing()

state = State()

def main(state):
    set_target_fps(60)
    create_board(state, num_mines, fixed_mines=True)
    init_window(screen_width, screen_height, "Minesweeper")
    while not window_should_close():
        update(state)
        render(state)

    close_window()

main(state)