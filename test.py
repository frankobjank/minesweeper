import random
import time
from pyray import *
from collections import deque
from datetime import date

# path to Python interpreter for pylance to recognize raylib/pyray
# /Users/jacobfrank/sources/minesweeper_rl/.venv/bin/python3

# Ideas from Google game:
    # make it so that you start on an empty square:
        # first selection is made
            # should not be able to flag until first move is made
        # create mines where each mine is at least 2 squares away from first selection
    
    # animate mines appearing when you die
        # could be annoying without the first fix though since it would happen too often




# game board constants
def initialize_board(difficulty):
    # width, height, num_mines
    if difficulty == "easy":
        w, h, num_mines = 10, 10, 10
    if difficulty == "medium":
        w, h, num_mines = 16, 16, 40
    if difficulty == "hard":
        w, h, num_mines = 30, 16, 99

    block = 30
    header_height=block*2
    screen_width=block*w
    screen_height=block*h+header_height

    board = {(x, y): Rectangle(x, y, block, block) for y in range(header_height, screen_height, block) for x in range(0, screen_width, block)}

    return screen_width, screen_height



set_target_fps(60)
display_menu = True

# from menu: continue to game, do nothing, or exit
def menu_test():
    init_window(300, 360, "Minesweeper")
    while not window_should_close():
        mouse = get_mouse_position()
        continue_button = Rectangle(0, 0, 300, 120)
        exit_button = Rectangle(0, 240, 300, 120)

        begin_drawing()
        clear_background(RAYWHITE)
        
        draw_rectangle_rec(continue_button, GREEN)
        draw_rectangle_rec(exit_button, RED)


        if is_mouse_button_released(MouseButton.MOUSE_BUTTON_LEFT): 
            if check_collision_point_rec(mouse, continue_button):
                print("go to game")
                draw_rectangle_lines_ex(continue_button, 3, BLACK)
                menu_state = "continue"
                break
            elif check_collision_point_rec(mouse, exit_button):
                draw_rectangle_lines_ex(exit_button, 3, BLACK)
                print("exit")
                menu_state = "exit"
            else:
                print("do nothing")
                break
        end_drawing()
    print("closing window")
    close_window()

    return menu_state

def window_test():
    menu_state = menu_test()
    if menu_state == "exit":
        return
    if menu_state == "continue":
        pass
    

    init_window(100, 100, "Window 2") # f"Minesweeper {difficulty}")

    while not window_should_close():
        mouse = get_mouse_position()
        button = Rectangle(40, 40, 20, 20)
        begin_drawing()
        clear_background(BLACK)
        draw_rectangle_rec(button, WHITE)

        if check_collision_point_rec(mouse, button):
            draw_rectangle_rec(button, GRAY)
            if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
                display_menu = True
                break
        end_drawing()
    close_window()
    # if display_menu == True:


window_test()

# I believe the issue of checking box twice has been resolved
# def code_test(x, y):
#     already_checked = set()
#     i = 1
#     already_checked.add((x, y))
#     to_reveal = []
#     while len(already_checked) < (screen_width//block*(screen_height-header_height)//block-1):
#         print(already_checked)
#         r = range(-i*block, i*block+1, block)
#         wholesquare = set((x+dx, y+dy) for dy in r for dx in r if (x+dx, y+dy) not in already_checked and 0<=x+dx<screen_width and header_height<=y+dy<screen_height)

#         outline = wholesquare.difference(already_checked)
#         already_checked = already_checked.union(outline)
#         for sq in outline:
#             to_reveal.append(sq)
#         i += 1



# Old non-recursive reveal
# def get_adjacent_not_recursive(self, state):
#     # could create sets for adj_to_mines and empty_squares
#     # so it's easier to know which squares should be revealed
#     # do pathfinder to get all empty squares connected to the self
#     # reveal all adjecents to empty_squares to get the adj_to_mines visible as well
#     state.to_reveal.appendleft(self)
#     i = 1
#     already_checked = set()
#     already_checked.add((self.x, self.y))
#     while len(already_checked) < (screen_width//block*(screen_height-header_height)//block-1):
#         r = range(-i*block, i*block+1, block)
#         whole_square = set(state.board[(self.x+dx, self.y+dy)] for dy in r for dx in r if (self.x+dx, self.y+dy) not in already_checked and 0<=self.x+dx<screen_width and header_height<=self.y+dy<screen_height)

#         outline = set(whole_square).difference(already_checked)
#         empty_squares = set()
#         for sq in outline:
#             if sq.adj > 0:
#                 continue
#             else:
#                 empty_squares.add(sq)
#         already_checked = already_checked.union(outline)
#         for sq in empty_squares:
#             state.to_reveal.appendleft(sq)
#         i += 1
