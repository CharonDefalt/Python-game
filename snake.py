import time
import random
import os
import sys

# --- Environment Detection and Input Module Selection ---
if os.name == 'nt':  # Windows
    try:
        import msvcrt
        # Function to get non-blocking key input on Windows
        def get_key_win():
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'w', b's', b'a', b'd', b'p', b'q'):
                    return key.decode().lower()
            return None
        HAS_CURSES = False
    except ImportError:
        HAS_CURSES = False
        def get_key_win(): return None
else:  # POSIX (Linux, Termux)
    try:
        import curses
        HAS_CURSES = True
        def get_key_win(): return None
    except ImportError:
        print("Error: 'curses' library not found. Please install it (e.g., pkg install python-curses in Termux).")
        sys.exit(1)

# --- Game Settings (Enlarged) ---
SNAKE_BODY_CHAR = '#' # Character for the snake body
SNAKE_HEAD_CHAR = ';' # Character for the snake head (as requested)
FOOD_CHAR = '*'
BOARD_WIDTH = 40
BOARD_HEIGHT = 20
INITIAL_SPEED = 0.15

# ANSI Color Sequences (for fallback)
RED_ANSI = '\033[91m'
RESET_ANSI = '\033[0m'


def initialize_curses(stdscr):
    """Initialize curses environment."""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) # Green for body
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Red for head/game over
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Yellow for pause


def place_food(snake, height, width, food_char):
    """Determine a random location for the food."""
    while True:
        food = [random.randint(1, height - 2), random.randint(1, width - 2)]
        if food not in snake:
            return food

def draw_border(stdscr, height, width):
    """Draw the game boundary."""
    for x in range(width):
        stdscr.addch(0, x, '#')
        stdscr.addch(height - 1, x, '#')
    for y in range(height):
        stdscr.addch(y, 0, '#')
        stdscr.addch(y, width - 1, '#')

def draw_game_state(stdscr, snake, food, score):
    """Draw all game elements on the screen."""
    stdscr.clear()
    draw_border(stdscr, BOARD_HEIGHT, BOARD_WIDTH)

    score_text = f"Score: {score}"
    stdscr.addstr(0, BOARD_WIDTH + 2, score_text)

    # Draw snake body (Green)
    for segment in snake[1:]:
        stdscr.addch(segment[0], segment[1], SNAKE_BODY_CHAR, curses.color_pair(1))
        
    # Draw snake head (Red '^')
    head = snake[0]
    stdscr.addch(head[0], head[1], SNAKE_HEAD_CHAR, curses.color_pair(2))


    # Draw food
    stdscr.addch(food[0], food[1], FOOD_CHAR)
    stdscr.refresh()

def display_pause_screen_curses(stdscr):
    """Display pause message in curses."""
    center_y = BOARD_HEIGHT // 2
    center_x = BOARD_WIDTH // 2
    
    pause_text = "PAUSED (Press P to continue)"
    stdscr.addstr(center_y, center_x - len(pause_text) // 2, pause_text, curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh()

def display_game_over_curses(stdscr, score):
    """Display game over message in red color in curses."""
    stdscr.clear()
    center_y = BOARD_HEIGHT // 2
    center_x = BOARD_WIDTH // 2

    game_over_text = "GAME OVER!"
    score_text = f"Final Score: {score}"

    stdscr.addstr(center_y, center_x - len(game_over_text) // 2, game_over_text, curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(center_y + 2, center_x - len(score_text) // 2, score_text)
    stdscr.addstr(center_y + 4, center_x - 10, "Exiting in 4 seconds...")
    stdscr.refresh()
    time.sleep(4)

def move_snake(snake, direction):
    """Calculate the new head position based on direction."""
    head = snake[0]
    new_head = list(head)
    if direction == 'w':
        new_head[0] -= 1
    elif direction == 's':
        new_head[0] += 1
    elif direction == 'a':
        new_head[1] -= 1
    elif direction == 'd':
        new_head[1] += 1
    
    snake.insert(0, new_head)

def check_collision(head, snake, height, width):
    """Check for boundary or self-collision."""
    # Boundary collision
    if head[0] <= 0 or head[0] >= height - 1 or head[1] <= 0 or head[1] >= width - 1:
        return True
    # Self collision (check against the rest of the body, excluding the new head position itself)
    if head in snake[1:]:
        return True
    return False

def play_game_curses(stdscr):
    """Main game loop using curses (real-time input)."""
    initialize_curses(stdscr)

    start_y = BOARD_HEIGHT // 2
    start_x = BOARD_WIDTH // 4
    # Initialize snake: Head is the first element [y, x]
    snake = [[start_y, start_x], [start_y, start_x - 1]]
    direction = 'd'
    food = place_food(snake, BOARD_HEIGHT, BOARD_WIDTH, FOOD_CHAR)
    score = 0
    is_paused = False
    game_over = False
    current_speed = INITIAL_SPEED

    while not game_over:
        # 1. Input handling
        key_input = None
        try:
            key = stdscr.getch()
            if key != -1:
                key_input = chr(key).lower()
        except:
            pass

        # 2. Handle Pause (P) and Quit (Q)
        if key_input == 'p':
            is_paused = not is_paused
            if is_paused:
                display_pause_screen_curses(stdscr)
            continue
        
        if key_input == 'q':
            game_over = True
            continue

        if is_paused:
            # If paused and no 'P' input, wait briefly
            time.sleep(0.1)
            continue

        # 3. Handle Movement (only when running)
        if key_input:
            if (key_input == 'w' and direction != 's') or \
               (key_input == 's' and direction != 'w') or \
               (key_input == 'a' and direction != 'd') or \
               (key_input == 'd' and direction != 'a'):
                direction = key_input

        # 4. Game Logic
        move_snake(snake, direction)
        head = snake[0]

        if check_collision(head, snake, BOARD_HEIGHT, BOARD_WIDTH):
            game_over = True
            continue

        if head == food:
            score += 10
            current_speed = max(0.05, INITIAL_SPEED - (score // 100) * 0.01)
            food = place_food(snake, BOARD_HEIGHT, BOARD_WIDTH, FOOD_CHAR)
        else:
            snake.pop()

        # 5. Render and Delay
        draw_game_state(stdscr, snake, food, score)
        time.sleep(current_speed)

    # Game Over sequence
    if game_over:
        display_game_over_curses(stdscr, score)


# --- Fallback (Windows/Basic CLI - Turn-based) ---

def print_board_fallback(snake, food):
    """Display the simple ASCII game board."""
    grid = [[' ' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    grid[food[0]][food[1]] = FOOD_CHAR
    # Draw body first (if head and body segment overlap, body character is drawn first)
    for y, x in snake[1:]:
        if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
            grid[y][x] = SNAKE_BODY_CHAR
            
    # Draw head last (to ensure it shows correctly)
    head_y, head_x = snake[0]
    if 0 <= head_y < BOARD_HEIGHT and 0 <= head_x < BOARD_WIDTH:
        grid[head_y][head_x] = SNAKE_HEAD_CHAR


    print("#" * (BOARD_WIDTH + 2))
    for y in range(BOARD_HEIGHT):
        row_str = "|"
        for x in range(BOARD_WIDTH):
            char_to_print = grid[y][x]
            
            if char_to_print == SNAKE_HEAD_CHAR:
                # Color head red in fallback
                row_str += f"{RED_ANSI}{char_to_print}{RESET_ANSI}"
            elif char_to_print == SNAKE_BODY_CHAR:
                # Keep body character as standard print (since ASCII doesn't support green body easily)
                row_str += char_to_print
            else:
                row_str += char_to_print
                
        row_str += "|"
        print(row_str)
    print("#" * (BOARD_WIDTH + 2))


def play_game_fallback():
    """Simple, turn-based Snake game (blocking input)."""
    snake = [[BOARD_HEIGHT // 2, BOARD_WIDTH // 4], [BOARD_HEIGHT // 2, BOARD_WIDTH // 4 - 1]]
    direction = 'd'
    food = place_food(snake, BOARD_HEIGHT, BOARD_WIDTH, FOOD_CHAR)
    score = 0
    is_paused = False

    while True:
        # 1. Display
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Score: {score} | Board Size: {BOARD_WIDTH}x{BOARD_HEIGHT}")
        
        if is_paused:
            print(f"{RED_ANSI}--- PAUSED (Press P to continue) ---{RESET_ANSI}")
        
        print_board_fallback(snake, food)

        # 2. Input handling (Blocking)
        print(f"Move (w/a/s/d), P to pause/resume, or q to quit: ", end="")
        
        move_input = input().lower()

        if move_input == 'q':
            print("Quitting game.")
            break
        
        # 3. Handle Pause
        if move_input == 'p':
            is_paused = not is_paused
            if not is_paused:
                time.sleep(0.5) 
            continue
        
        if is_paused:
            print("Game is paused. Press P to resume.")
            time.sleep(0.5)
            continue

        # 4. Handle Movement
        if move_input in ['w', 'a', 's', 'd']:
            if (move_input == 'w' and direction != 's') or \
               (move_input == 's' and direction != 'w') or \
               (move_input == 'a' and direction != 'd') or \
               (move_input == 'd' and direction != 'a'):
                direction = move_input
        else:
            print("Invalid move, press ENTER to continue...")
            time.sleep(0.5)
            continue

        # 5. Game Logic
        move_snake(snake, direction)
        head = snake[0]

        # 6. Collision Check
        if check_collision(head, snake, BOARD_HEIGHT, BOARD_WIDTH):
            os.system('cls' if os.name == 'nt' else 'clear')
            print_board_fallback(snake, food)
            print(f"{RED_ANSI}\nGAME OVER! Final Score: {score}{RESET_ANSI}")
            print("Exiting in 4 seconds...")
            time.sleep(4)
            break

        # 7. Food Check
        if head == food:
            score += 10
            food = place_food(snake, BOARD_HEIGHT, BOARD_WIDTH, FOOD_CHAR)
        else:
            snake.pop()


# --- Game Execution ---
if __name__ == "__main__":
    if HAS_CURSES:
        try:
            import curses
            curses.wrapper(play_game_curses)
        except Exception as e:
            print(f"An error occurred during curses execution: {e}")
    elif os.name == 'nt':
        # Windows execution path (using turn-based fallback)
        play_game_fallback()
    else:
        # Termux/Linux execution path (without curses, using turn-based fallback)
        play_game_fallback()

