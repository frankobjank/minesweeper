import random
import time
from pyray import *
from collections import deque

# game board constants
block = 30
header_height=block*2
screen_width=block*10
screen_height=block*10+header_height
num_mines = 10
# board_borders = 0 <= x <= screen_width; header_height <= y <= screen_height
# board_borders = 0 <= x <= 300         ;            60 <= y <= 360

# header buttons + boxes
header_box = Rectangle(screen_width//18, 8, block*2, block+block//2) # timer and mines_remaining
reset_button = Rectangle(screen_width//2-(block*2), block//2, block*4, block)

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
        return f"Square at ({self.x}, {self.y}), mine = {self.mine}, adj = {self.adj}"
    
    # get number of adjacent mines but not mines themselves. Make sure it's in range i.e. .get()
    def get_adjacent_to_mines(self, state):
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x+dx, self.y+dy), None)
                if adj != None and adj != self and adj.mine == False:
                    adj.adj += 1

    # get adjacent not-visible squares that aren't mines or flags
    def get_adjacent_recursive(self, state):
        state.to_reveal.appendleft(self)
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x+dx, self.y+dy), None)
                if adj != None and adj != self and adj.visible == False and adj not in state.to_reveal:
                    state.to_reveal.appendleft(adj)
                    if adj.adj == 0: # if adj is empty, run again
                        adj.get_adjacent_recursive(state)
    
    def get_adjacent_not_recursive(self, state):
        pass

    def get_neighbors(self, state):
        neighbors = set()
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x+dx, self.y+dy), None)
                if adj != None and adj != self:
                    neighbors.add(adj)

        return neighbors


class State:
    def __init__(self):
        self.board_rectangle = Rectangle(0, header_height, screen_width, screen_height)
        self.board = {}
        # board elements
        self.mines = set()
        self.adjacent_to_mines = set()
        self.empty_squares_paths = set()

        self.flags = set()
        self.mines_remaining = num_mines - len(self.flags)
        self.selection = None
        self.to_reveal = deque() # for animating reveal
        self.revealing_square = None # for animating reveal
        self.origin = None # for animating reveal
        self.frame_count = 0 # for animating reveal
        self.win = False
        self.lose = False
        self.reset = False
        self.start_clock = False
        self.start_time = get_time()
        self.game_time = 0
        self.score = 0
    
    def get_game_time(self):
        return get_time() - self.start_time

def update_menu(state):
    pass

def render_menu(state):
    pass

def reset():
    new_state = State()
    create_board(new_state, num_mines, fixed_mines=True)
    return new_state

def create_board(state, num_mines, fixed_mines=False):
    state.board = {(x, y): Square(x, y) for y in range(header_height, screen_height, block) for x in range(0, screen_width, block)}
    # fixed_mines mines for debugging
    if fixed_mines == True:
        state.mines = set(state.board[(mine_coord)] for mine_coord in [(30, 60), (180, 120), (60, 90), (0, 150), (210, 150), (90, 180), (210, 180), (0, 210), (60, 210), (60, 270)])

        for mine in state.mines:
            state.board[(mine.x, mine.y)].mine = True
    # random mines
    else:
        while len(state.mines)<num_mines:
            mine = (get_random_coords())
            state.mines.add(state.board[(mine.x, mine.y)])
            state.board[(mine.x, mine.y)].mine = True

    # calc adj to mines
    for mine in state.mines:
        mine.get_adjacent_to_mines(state)
    empty_squares = []
    for coord, sq in state.board.items():
        if sq.mine == False:
            if sq.adj > 0:
                state.adjacent_to_mines.add(sq)
            else:
                empty_squares.append(sq)
    # for sq in empty_squares:
    #     while empty_squares:
    #         compare = empty_squares.pop()
    #         if (sq.x+30, sq.y) == (compare.x, compare.y):


def update(state):
    state.frame_count += 1
    if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT): # hold down left click
        state.selection = get_mouse_position()
        # check if selection is on board and game isn't over. for some reason game crashes when mouse selection goes above the game window
        if 0<state.selection.x<screen_width and 0<state.selection.y<screen_height and state.lose == False and state.win == False:
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

    elif is_mouse_button_down(MouseButton.MOUSE_BUTTON_RIGHT): # hold down right click 
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

    elif is_mouse_button_released(MouseButton.MOUSE_BUTTON_LEFT): # release left click
        if state.selection == "reset":
            state.reset = True
            return
        elif state.selection != None:
            if state.selection.flag == True: # if flag
                pass
            elif state.selection.mine == True: # if mine
                state.lose = True
                state.selection.blow_up = True
                state.score = state.get_game_time() # game over, freeze time
            elif state.selection.adj > 0: # if revealing a number
                state.selection.visible = True
                state.selection = None
            else: # empty space, recursive reveal
                state.selection.visible = True
                state.selection.get_adjacent_recursive(state)
                # state.selection.get_adjacent_not_recursive(state)
                state.selection = None

    elif is_mouse_button_released(MouseButton.MOUSE_BUTTON_RIGHT): # release right click
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
            
    state.mines_remaining = num_mines - len(state.flags)

    # remove to_reveal one-by-one displaced by % frames and convert to visible squares
    if state.revealing_square:
        state.revealing_square.visible = True
    if state.to_reveal:
        if state.frame_count % 2 == 0:
            state.revealing_square = state.to_reveal.pop()
    else:
        state.revealing_square = None

    
    # check for win 2 ways: if set(mines) matches set(flags)
    if state.win == False and state.lose == False:
        if state.flags == state.mines:
            state.win = True
            state.score = state.get_game_time() # game over, freeze time
        # if all non-mines are visible
        if all(square.visible == True for square in state.board.values() if square.mine == False):
            state.win = True
            state.score = state.get_game_time() # game over, freeze time
            # flag all mines not yet flagged
            for mine in state.mines:
                if mine.flag == False:
                    mine.flag = True
                    state.flags.add(mine)

    # don't start clock until square is revealed
    if state.start_clock == False:
        state.start_time = get_time()
        for square in state.board.values():
            if square.visible == True:
                state.start_clock = True
                break

    # calc game time
    if state.win == False and state.lose == False:
        state.game_time = str(int(state.get_game_time()))
    else:
        state.game_time = str(int(state.score))



    # for debugging - press m to reveal
    if is_key_pressed(KeyboardKey.KEY_M):
        print(f"{state.selection}")


def render(state):
    begin_drawing()
    clear_background(LIGHTGRAY)
    # draw squares in board
    for square in state.board.values():
        if square.flag == True: # flags don't change until deselected
            draw_rectangle(square.x, square.y, 30, 30, BLUE)
        elif square == state.selection: # mouse pressed down but not released
            draw_rectangle(state.selection.x, state.selection.y, 30, 30, LIGHTGRAY)
        elif square == state.revealing_square:
            draw_rectangle(square.x, square.y, 30, 30, WHITE)
        elif square.visible == True:
            draw_rectangle(square.x, square.y, 30, 30, GREEN) # fill safe squares with green
            if square.adj == 1: # squares with 1; diff offset due to font size
                draw_text(str(square.adj), square.x+12, square.y+5, 20, BLACK)
            if square.adj > 1: # number squares above 1; diff offset due to font size
                draw_text(str(square.adj), square.x+10, square.y+5, 20, BLACK)
        else: # unselected/ unrevealed
            draw_rectangle(square.x, square.y, 30, 30, DARKGRAY)
    
    
    # draw timer on left
    draw_rectangle(int(header_box.x), int(header_box.y), int(header_box.width), int(header_box.height), BLACK)
    len_time = len(state.game_time)
    draw_text(state.game_time, int(header_box.x+header_box.width//(2+len_time)), 20, 25, WHITE)

    # draw mines remaining on the right
    draw_rectangle(screen_width-int(header_box.x)-int(header_box.width), int(header_box.y), int(header_box.width), int(header_box.height), BLACK)
    len_min_rem = len(str(state.mines_remaining))
    draw_text(str(state.mines_remaining), screen_width-int(header_box.width//2)-int(header_box.x+header_box.width//(2+len_min_rem)), 20, 25, WHITE)


    # header_box =   Rectangle(screen_width//18,          8,        block*2, block+block//2)

    # reset_button = Rectangle(screen_width//2-(block*2), block//2, block*4, block         )

    # draw reset button, depending on state.win
    
    # draw_rectangle(int(reset_button.x), int(reset_button.y), int(reset_button.width), int(reset_button.height), GRAY)
    if state.win != True:
        draw_text("Reset", screen_width//2-block-4, 20, 25, BLACK)
    elif state.win == True:
        draw_text("Congrats!!!!", screen_width//2-block-25, 20, 20, BLACK)

    # if state.lose, x out flags and reveal mines
    if state.lose == True:
        render_lose(state)

    draw_grid()

    end_drawing()


def render_lose(state):
    for mine in state.mines:
        if mine.blow_up == True: # orange if the killing blow
            draw_rectangle(mine.x, mine.y, 30, 30, ORANGE)
        elif mine.flag == True: # pass over flagged mines
            pass
        else: # reveal all non-flagged mines
            draw_rectangle(mine.x, mine.y, 30, 30, RED)
    
    for flag in state.flags:
        if flag.mine == False: # if wrongly flagged, X-out
            draw_line_ex((flag.x, flag.y), (flag.x+block, flag.y+block), 2, RED)
            draw_line_ex((flag.x, flag.y+block), (flag.x+block, flag.y), 2, RED)


def draw_grid():
    for x in range(0, screen_width, block):
        draw_line(x, header_height, x, screen_height, BLACK)
    for y in range(header_height, screen_height, block):
        draw_line(0, y, screen_width, y, BLACK)


def main():
    state = State()
    set_target_fps(60)
    create_board(state, num_mines, fixed_mines=True)
    init_window(screen_width, screen_height, "Minesweeper")
    while not window_should_close():
        update(state)
        render(state)

        # reset game if button pressed
        if state.reset == True:
            state = reset()
    close_window()

main()

# to-do:
# only start timer after first move, clock_start variable?
# save high-scores
# more difficulties and window sizing
    # for incorporating medium and hard, start with menu to choose difficulty
    # then use set_window_size based on selection
