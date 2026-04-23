import random
import pyray as pr
from collections import deque


def set_dimensions(difficulty: str) -> tuple[int, int, int]:
    # width, height, num_mines
    if difficulty == "medium":
        return 16, 16, 40
    elif difficulty == "hard":
        return 30, 16, 99
    return 10, 10, 10


w, h, num_mines = set_dimensions("easy")

# game board constants
block = 30
header_height = block * 2
screen_width = block * w
screen_height = block * h + header_height

# board_borders = 0 <= x <= screen_width; header_height <= y <= screen_height
# board_borders = 0 <= x <= 300         ;            60 <= y <= 360

# header buttons + boxes
header_box = pr.Rectangle(
    screen_width // 18, 8, block * 2, block + block // 2
)  # timer and mines_remaining
reset_button = pr.Rectangle(
    screen_width // 2 - (block * 1.5), block // 2, block * 3, block
)
# animate_button = pr.Rectangle(screen_width//2-block*2.5, block//2, block, block)


def get_random_coords():
    return pr.Vector2(
        random.randrange(0, screen_width, 30),
        random.randrange(header_height, screen_height, 30),
    )


class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.adj = 0  # adj to mines number
        self.mine = False
        self.flag = False
        self.visible = False
        self.rectangle = pr.Rectangle(self.x, self.y, block, block)
        self.blow_up = False

    def __repr__(self):
        return f"Square at ({self.x}, {self.y}), mine = {self.mine}, adj = {self.adj}"

    # get number of adjacent mines but not mines themselves. Make sure it's in range i.e. .get()
    def get_adjacent_to_mines(self, state):
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x + dx, self.y + dy), None)
                if adj is not None and adj != self and not adj.mine:
                    adj.adj += 1

    # get adjacent not-visible squares that aren't mines or flags
    def get_adjacent_recursive_animation(self, state):
        state.to_reveal.appendleft(self)
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x + dx, self.y + dy), None)
                if (
                    adj is not None
                    and adj != self
                    and not adj.visible
                    and adj not in state.to_reveal
                ):
                    state.to_reveal.appendleft(adj)
                    if adj.adj == 0:  # if adj is empty, run again
                        adj.get_adjacent_recursive_animation(state)

    def get_adjacent_recursive(self, state):
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x + dx, self.y + dy), None)
                if adj is not None and adj != self and not adj.visible:
                    adj.visible = True
                    if adj.adj == 0:  # if adj is empty, run again
                        adj.get_adjacent_recursive(state)

    def get_adjacent_not_recursive(self, state):
        pass

    def get_neighbors(self, state):
        neighbors = set()
        for dy in [-block, 0, block]:
            for dx in [-block, 0, block]:
                adj = state.board.get((self.x + dx, self.y + dy), None)
                if adj is not None and adj != self:
                    neighbors.add(adj)

        return neighbors


class State:
    def __init__(self):
        self.board_rectangle = pr.Rectangle(
            0, header_height, screen_width, screen_height
        )

        # (int, int) tuple as type hint key creates warning but works
        self.board = {}  # dict[(int, int), Square]
        # board elements
        self.mines = set()
        self.adjacent_to_mines = set()
        self.empty_squares_paths = set()

        self.flags: set[Square] = set()
        self.mines_remaining = num_mines - len(self.flags)
        self.selection: pr.Vector2 | str | Square | None = None
        self.win = False
        self.lose = False
        self.reset = False
        self.start_clock = False
        self.start_time = pr.get_time()
        self.game_time = ""
        self.score = 0

        self.animate = True
        self.to_reveal = deque()  # for animating reveal
        self.revealing_square = None  # for animating reveal
        self.origin = None  # for animating reveal
        self.frame_count = 0  # for animating reveal

    # Was converting to int for all use cases so will return as int
    def get_game_time(self) -> int:
        return int(pr.get_time() - self.start_time)


def update_menu():
    pass


def render_menu(state):
    pr.draw_text(
        "Minesweeper",
        (screen_width - pr.measure_text("Minesweeper", 16)) // 2,
        10,
        16,
        pr.BLACK,
    )


def reset():
    new_state = State()
    create_board(new_state, num_mines)  # , fixed_mines=True)
    return new_state


def create_board(state, num_mines, fixed_mines=False):
    state.board = {
        (x, y): Square(x, y)
        for y in range(header_height, screen_height, block)
        for x in range(0, screen_width, block)
    }
    # fixed_mines mines for debugging
    if fixed_mines:
        state.mines = set(
            state.board[(mine_coord)]
            for mine_coord in [
                (30, 60),
                (180, 120),
                (60, 90),
                (0, 150),
                (210, 150),
                (90, 180),
                (210, 180),
                (0, 210),
                (60, 210),
                (60, 270),
            ]
        )

        for mine in state.mines:
            state.board[(mine.x, mine.y)].mine = True
    # random mines
    else:
        while len(state.mines) < num_mines:
            mine = get_random_coords()
            state.mines.add(state.board[(mine.x, mine.y)])
            state.board[(mine.x, mine.y)].mine = True

    # calc adj to mines
    for mine in state.mines:
        mine.get_adjacent_to_mines(state)
    empty_squares = []
    for coord, sq in state.board.items():
        if not sq.mine:
            if sq.adj > 0:
                state.adjacent_to_mines.add(sq)
            else:
                empty_squares.append(sq)
    # for sq in empty_squares:
    #     while empty_squares:
    #         compare = empty_squares.pop()
    #         if (sq.x+30, sq.y) == (compare.x, compare.y):


def update(state: State):
    state.frame_count += 1
    if pr.is_mouse_button_down(
        pr.MouseButton.MOUSE_BUTTON_LEFT
    ):  # hold down left click
        state.selection = pr.get_mouse_position()
        # check if selection is on board and game isn't over. for some reason game crashes when mouse selection goes above the game window
        if (
            0 < state.selection.x < screen_width
            and header_height < state.selection.y < screen_height
            and not state.lose
            and not state.win
        ):
            state.selection.x -= state.selection.x % 30
            state.selection.y -= state.selection.y % 30
            state.selection = state.board.get(
                (state.selection.x, state.selection.y), None
            )
            # Check selection is a Square
            if isinstance(state.selection, Square) and (
                state.selection.visible or state.selection.flag
            ):  # if flag or visible
                state.selection = None
        # check if selection on reset button, works even if game is over
        elif pr.check_collision_point_rec(state.selection, reset_button):
            state.selection = "reset"
        else:
            state.selection = None

    elif pr.is_mouse_button_down(
        pr.MouseButton.MOUSE_BUTTON_RIGHT
    ):  # hold down right click
        state.selection = pr.get_mouse_position()
        # check if selection on board and game isn't over
        if (
            pr.check_collision_point_rec(state.selection, state.board_rectangle)
            and not state.lose
            and not state.win
        ):
            state.selection.x -= state.selection.x % 30
            state.selection.y -= state.selection.y % 30
            state.selection = state.board.get(
                (state.selection.x, state.selection.y), None
            )
            if (
                isinstance(state.selection, Square) and state.selection.visible
            ):  # (allows selection of flags)
                state.selection = None
        # check if selection on reset button, works even if game is over
        elif pr.check_collision_point_rec(state.selection, reset_button):
            state.selection = "reset"
        else:
            state.selection = None

    elif pr.is_mouse_button_released(
        pr.MouseButton.MOUSE_BUTTON_LEFT
    ):  # release left click
        if state.selection == "reset":
            state.reset = True
            return
        # Check if selection is a Square
        elif isinstance(state.selection, Square):
            if state.selection.flag:  # if flag
                pass
            elif state.selection.mine:  # if mine
                state.lose = True
                state.selection.blow_up = True
                state.score = state.get_game_time()  # game over, freeze time
            elif state.selection.adj > 0:  # if revealing a number
                state.selection.visible = True
                state.selection = None
            else:  # empty space, recursive reveal
                state.selection.visible = True
                # state.selection.get_adjacent_recursive(state)
                # state.selection.get_adjacent_not_recursive(state)
                # ANIMATION OPTION
                state.selection.get_adjacent_recursive_animation(state)
                state.selection = None

    elif pr.is_mouse_button_released(
        pr.MouseButton.MOUSE_BUTTON_RIGHT
    ):  # release right click
        if state.selection == "reset":
            state.reset = True
            return
        if isinstance(state.selection, Square) and not state.selection.visible:
            if not state.selection.flag:
                state.selection.flag = True
                state.flags.add(state.selection)
                state.selection = None

            elif state.selection.flag:
                state.selection.flag = False
                state.flags.remove(state.selection)
                state.selection = None

    # F key can also flag and unflag to get around mac right click issues
    elif pr.is_key_pressed(pr.KeyboardKey.KEY_F):
        state.selection = pr.get_mouse_position()
        # check if selection on board and game isn't over
        if (
            pr.check_collision_point_rec(state.selection, state.board_rectangle)
            and not state.lose
            and not state.win
        ):
            state.selection.x -= state.selection.x % 30
            state.selection.y -= state.selection.y % 30
            state.selection = state.board.get(
                (state.selection.x, state.selection.y), None
            )
            if (
                isinstance(state.selection, Square) and state.selection.visible
            ):  # (allows selection of flags)
                state.selection = None

        if isinstance(state.selection, Square) and not state.selection.visible:
            if not state.selection.flag:
                state.selection.flag = True
                state.flags.add(state.selection)
                state.selection = None
            elif state.selection.flag:
                state.selection.flag = False
                state.flags.remove(state.selection)
                state.selection = None

    state.mines_remaining = num_mines - len(state.flags)

    # ANIMATION OPTION
    # remove to_reveal one-by-one displaced by % frames and convert to visible squares
    if state.revealing_square:
        state.revealing_square.visible = True
    if state.to_reveal:
        # speed of reveal
        if state.frame_count % 2 == 0:
            state.revealing_square = state.to_reveal.pop()
    else:
        state.revealing_square = None

    # check for win 2 ways: if set(mines) matches set(flags)
    if not state.win and not state.lose:
        if state.flags == state.mines:
            state.win = True
            state.score = state.get_game_time()  # game over, freeze time
        # if all non-mines are visible
        if all(square.visible for square in state.board.values() if not square.mine):
            state.win = True
            state.score = state.get_game_time()  # game over, freeze time
            # flag all mines not yet flagged
            for mine in state.mines:
                if not mine.flag:
                    mine.flag = True
                    state.flags.add(mine)

    # don't start clock until first square is revealed
    if not state.start_clock:
        state.start_time = pr.get_time()
        for square in state.board.values():
            if square.visible:
                state.start_clock = True
                break

    # calc game time
    if not state.win and not state.lose:
        state.game_time = str(state.get_game_time())
    else:
        state.game_time = str(state.score)


def render(state):
    pr.begin_drawing()
    pr.clear_background(pr.LIGHTGRAY)
    # draw squares in board
    for square in state.board.values():
        if square.flag:  # flags don't change until deselected
            pr.draw_rectangle(square.x, square.y, 30, 30, pr.BLUE)
        elif square == state.selection:  # mouse pressed down but not released
            pr.draw_rectangle(
                state.selection.x, state.selection.y, 30, 30, pr.LIGHTGRAY
            )
        # ANIMATION OPTION
        elif square == state.revealing_square:
            pr.draw_rectangle(square.x, square.y, 30, 30, pr.WHITE)
        elif square.visible:
            pr.draw_rectangle(
                square.x, square.y, 30, 30, pr.GREEN
            )  # fill safe squares with green
            if square.adj == 1:  # squares with 1; diff offset due to font size
                pr.draw_text(str(square.adj), square.x + 12, square.y + 5, 20, pr.BLACK)
            if square.adj > 1:  # number squares above 1; diff offset due to font size
                pr.draw_text(str(square.adj), square.x + 10, square.y + 5, 20, pr.BLACK)
        else:  # unselected/ unrevealed
            pr.draw_rectangle(square.x, square.y, 30, 30, pr.DARKGRAY)

    # draw timer on left
    pr.draw_rectangle(
        int(header_box.x),
        int(header_box.y),
        int(header_box.width),
        int(header_box.height),
        pr.BLACK,
    )
    len_time = len(state.game_time)
    pr.draw_text(
        state.game_time,
        int(header_box.x + header_box.width // (2 + len_time)),
        20,
        25,
        pr.WHITE,
    )

    # draw mines remaining on the right
    pr.draw_rectangle(
        screen_width - int(header_box.x) - int(header_box.width),
        int(header_box.y),
        int(header_box.width),
        int(header_box.height),
        pr.BLACK,
    )
    len_min_rem = len(str(state.mines_remaining))
    pr.draw_text(
        str(state.mines_remaining),
        screen_width
        - int(header_box.width // 2)
        - int(header_box.x + header_box.width // (2 + len_min_rem)),
        20,
        25,
        pr.WHITE,
    )

    # header_box =   pr.Rectangle(screen_width//18,          8,        block*2, block+block//2)

    # reset_button = pr.Rectangle(screen_width//2-(block*2), block//2, block*4, block         )

    # draw reset button, depending on state.win
    if state.selection == "reset":
        pr.draw_rectangle(
            int(reset_button.x),
            int(reset_button.y),
            int(reset_button.width),
            int(reset_button.height),
            pr.BLACK,
        )
        if not state.win:
            pr.draw_text("Reset", screen_width // 2 - block - 4, 20, 25, pr.WHITE)
        elif state.win:
            pr.draw_text("Good job!", screen_width // 2 - block - 15, 20, 20, pr.WHITE)

    else:
        pr.draw_rectangle(
            int(reset_button.x),
            int(reset_button.y),
            int(reset_button.width),
            int(reset_button.height),
            pr.GRAY,
        )
        if not state.win:
            pr.draw_text("Reset", screen_width // 2 - block - 4, 20, 25, pr.BLACK)
        elif state.win:
            pr.draw_text("Good job!", screen_width // 2 - block - 15, 20, 20, pr.BLACK)

    # draw_rectangle(int(animate_button.x), int(animate_button.y), int(animate_button.width), int(animate_button.height), RED)

    # if state.lose, x out flags and reveal mines
    if state.lose:
        render_lose(state)

    # draw_grid
    for x in range(0, screen_width, block):
        pr.draw_line(x, header_height, x, screen_height, pr.BLACK)
    for y in range(header_height, screen_height, block):
        pr.draw_line(0, y, screen_width, y, pr.BLACK)

    pr.end_drawing()


def render_lose(state: State):
    for mine in state.mines:
        if mine.blow_up:  # orange if the killing blow
            pr.draw_rectangle(mine.x, mine.y, 30, 30, pr.ORANGE)
        elif mine.flag:  # pass over flagged mines
            pass
        else:  # reveal all non-flagged mines
            pr.draw_rectangle(mine.x, mine.y, 30, 30, pr.RED)

    for flag in state.flags:
        if not flag.mine:  # if wrongly flagged, X-out
            # Called Vector2 constructor for type
            pr.draw_line_ex(
                pr.Vector2(flag.x, flag.y),
                pr.Vector2(flag.x + block, flag.y + block),
                2,
                pr.RED,
            )
            pr.draw_line_ex(
                pr.Vector2(flag.x, flag.y + block),
                pr.Vector2(flag.x + block, flag.y),
                2,
                pr.RED,
            )


def main():
    state = State()
    pr.set_target_fps(60)
    create_board(state, num_mines)  # , fixed_mines=True)
    pr.init_window(screen_width, screen_height, "Minesweeper")
    while not pr.window_should_close():
        update(state)
        render(state)

        # reset game if button pressed
        if state.reset:
            state = reset()
    pr.close_window()


main()

# to-do:
# save high-scores
# more difficulties and window sizing
# for incorporating medium and hard, start with menu to choose difficulty
# then use set_window_size based on selection
