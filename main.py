import random
import time
from pyray import *

# for incorporating medium and hard, start with menu to choose difficulty
# then use set_window_size based on selection

BLOCK = 30
header_height=BLOCK*2
screen_width=BLOCK*10
screen_height=BLOCK*10+header_height
num_mines = 10

init_window(screen_width, screen_height, "Minesweeper")
set_target_fps(60)

while not window_should_close():
    begin_drawing()
    clear_background(LIGHTGRAY)
    # render
    for x in range(0, screen_width, BLOCK):
        draw_line(x, header_height, x, screen_height, BLACK)
    for y in range(header_height, screen_height, BLOCK):
        draw_line(0, y, screen_width, y, BLACK)
    
    end_drawing()
close_window()