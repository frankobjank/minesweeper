import random
import time
from pyray import *

# for incorporating medium and hard, start with menu to choose difficulty
# then use set_window_size based on selection
# globals
mouse_button_left= 0
mouse_button_right= 1
key_m= 77

block = 30
header_height=block*2
screen_width=block*10
screen_height=block*10+header_height
num_mines = 10
reset_button = Rectangle(screen_width//2-block, block//2, block*2, block,)

def get_random_coords():
    return Vector2(random.randrange(0, screen_width, 30), random.randrange(header_height, screen_height, 30))

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.adj = 0 # adj to mines number
        self.mine = False
        self.flag = False
        self.visible = False
        self.rectangle = Rectangle(self.x, self.y, block, block)
        self.blow_up = False

    def __repr__(self):
        return f"({self.x}, {self.y}), mine = {self.mine}, flag = {self.flag}, visible = {self.visible}"
    
    def get_adjacent(self, state):
        return [state.board[(x, y)] for y in range(-block, 0, block) for x in range(-block, 0, block)]

class State:
    def __init__(self):
        self.board = {}
        self.board_rectangle = Rectangle(0, header_height, screen_width, screen_height)
        self.mines = set()
        self.visible_squares = set()
        self.flags = set()
        self.selection = None
        self.lose = False
        self.win = False
        self.reset = False

    

def reset():
    new_state = State()
    create_board(new_state, num_mines, fixed_mines=False)
    return new_state


def create_board(state, num_mines, fixed_mines=False):
    state.board = {(x, y): Square(x, y) for y in range(header_height, screen_height, block) for x in range(0, screen_width, block)}
    # fixed_mines mines for debugging
    if fixed_mines == True:
        state.mines = [(30, 60), (180, 60), (60, 90), (0, 150), (210, 150), (90, 180), (270, 180), (0, 210), (60, 210), (60, 270)]
        for mine in state.mines:
            state.board[(mine)].mine = True
    # random mines
    else:
        while len(state.mines)<num_mines:
            mine = (get_random_coords())
            state.mines.add(state.board[(mine.x, mine.y)])
            state.board[(mine.x, mine.y)].mine = True

    # # calc adj to mines
    # for mine in state.mines:
    #     # print((mine.x, mine.y)) # for debugging
    #     all_adjacent = mine.get_adjacent(state, exclude="mine")
    #     for adj in all_adjacent:
    #         adj.adj += 1

# could change all squares to Rectangles if you can get them to be structs
# easier to calculate collision if no modulo


# check_collision_point_rec(point: Vector2, rec: Rectangle)


def update(state):

    if is_mouse_button_down(mouse_button_left): # hold down left click
        state.selection = get_mouse_position()
        # check if selection is on board and game isn't over
        if check_collision_point_rec(state.selection, state.board_rectangle) == True and state.lose == False and state.win == False:
            state.selection.x -= state.selection.x % 30
            state.selection.y -= state.selection.y % 30
            state.selection = state.board.get((state.selection.x, state.selection.y), None)
            if state.selection.visible == True or state.selection.flag == True: # if flag or visible
                state.selection = None
        # check if selection on reset button, works even if game is over
        elif check_collision_point_rec(state.selection, reset_button) == True:
            state.selection = "reset"
        else:
            state.selection = None


    elif is_mouse_button_down(mouse_button_right): # hold down right click 
        state.selection = get_mouse_position()
        # check if selection on board and game isn't over
        if check_collision_point_rec(state.selection, state.board_rectangle) == True and state.lose == False and state.win == False:
            state.selection.x -= state.selection.x % 30
            state.selection.y -= state.selection.y % 30
            state.selection = state.board.get((state.selection.x, state.selection.y), None)
            if state.selection.visible == True: # (allows selection of flags)
                state.selection = None
        # check if selection on reset button, works even if game is over
        elif check_collision_point_rec(state.selection, reset_button) == True:
            state.selection = "reset"
        else:
            state.selection = None

    elif is_mouse_button_released(mouse_button_left): # release left click
        if state.selection == "reset":
            state.reset = True
            return
        elif state.selection != None:
            if state.selection.flag == False: # if not a flag
                if state.selection.mine == True:
                    state.lose = True
                    state.selection.blow_up = True
                elif state.selection.adj > 0:
                    pass
                else: # if revealing a number
                    state.selection.visible = True
                    state.visible_squares.add(state.selection)
                    state.selection = None

    elif is_mouse_button_released(mouse_button_right): # release right click
        if state.selection == "reset":
            state.reset = True
            return
        if state.selection != None and state.selection.visible == False:
            if state.selection.flag == False:
                state.selection.flag = True
                state.flags.add(state.selection)
                state.selection = None

            elif state.selection.flag == True:
                state.selection.flag = False
                state.flags.remove(state.selection)
                state.selection = None
    
    # for debugging - press m to reveal
    if is_key_pressed(key_m):
        print(state.reset)

def render(state):
    begin_drawing()
    clear_background(LIGHTGRAY)
    # draw squares in board
    for square in state.board.values():
        if square.flag == True: # flags don't change until deselected
            draw_rectangle(square.x, square.y, 30, 30, BLUE)
        elif square == state.selection:
            draw_rectangle(state.selection.x, state.selection.y, 30, 30, LIGHTGRAY)
        elif square.visible == True:
            draw_rectangle(square.x, square.y, 30, 30, GREEN)
        # debugging - display where mines are
        # elif square.mine == True:
        #     draw_rectangle(square.x, square.y, 30, 30, RED)
        else:
            draw_rectangle(square.x, square.y, 30, 30, DARKGRAY)
    
    if state.lose == True:
        for mine in state.mines:
            draw_rectangle(mine.x, mine.y, 30, 30, RED)
            if mine.blow_up == True:
                draw_rectangle(mine.x, mine.y, 30, 30, ORANGE)
    elif state.win == True:
        pass
    
    draw_grid()

    # draw reset button
    draw_rectangle(int(reset_button.x), int(reset_button.y), block*2, block, GRAY)
    draw_text("Reset", screen_width//2-block+5, 20, 19, BLACK)
    end_drawing()


def render_win(state):
    pass

def draw_grid():
    for x in range(0, screen_width, block):
        draw_line(x, header_height, x, screen_height, BLACK)
    for y in range(header_height, screen_height, block):
        draw_line(0, y, screen_width, y, BLACK)


def main():
    state = State()
    set_target_fps(60)
    create_board(state, num_mines, fixed_mines=False)
    init_window(screen_width, screen_height, "Minesweeper")
    while not window_should_close():
        update(state)
        render(state)

        # reset game after win or lose
        if state.reset == True:
            state = reset()
    close_window()

main()

# track time
# save high-scores
# display mines left