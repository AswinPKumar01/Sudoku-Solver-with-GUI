import random
import time
from concurrent.futures import ThreadPoolExecutor

def valid_move_check(board, num, pos):
    row, col = pos

    if num in board[row] or num in set(board[i][col] for i in range(len(board))):
        return False

    box_start_row, box_start_col = 3 * (row // 3), 3 * (col // 3)

    if num in set(board[i][j] for i in range(box_start_row, box_start_row + 3) for j in range(box_start_col, box_start_col + 3)):
        return False

    return True

def dynamic_parallel_sudoku_solver(board, max_workers=9):
    with ThreadPoolExecutor(max_workers=min(max_workers, len(board))) as executor:
        futures = []

        for num in range(1, 10):
            empty_cell = heuristic_find_empty_cell(board)
            if empty_cell and valid_move_check(board, num, empty_cell):
                board_copy = [row[:] for row in board]
                board_copy[empty_cell[0]][empty_cell[1]] = num
                futures.append(executor.submit(sudoku_solver, board_copy))

        for future in futures:
            if future.result():
                return True

        return False

def heuristic_find_empty_cell(board):
    empty_cells = [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == 0]
    if not empty_cells:
        return None

    empty_cells.sort(key=lambda pos: len(valid_moves(board, pos)))
    return empty_cells[0]

def valid_moves(board, pos):
    row, col = pos
    possible_values = set(range(1, 10))

    possible_values -= set(board[row])
    possible_values -= set(board[i][col] for i in range(len(board)))

    box_start_row, box_start_col = 3 * (row // 3), 3 * (col // 3)
    possible_values -= set(board[i][j] for i in range(box_start_row, box_start_row + 3) for j in range(box_start_col, box_start_col + 3))

    return possible_values

def sudoku_solver(board):
    def find_empty_cell():
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    return i, j
        return None

    empty_cell = find_empty_cell()

    if not empty_cell:
        return True
    else:
        row, col = empty_cell

    for num in range(1, 10):
        if valid_move_check(board, num, (row, col)):
            board[row][col] = num

            if sudoku_solver(board):
                return True

            board[row][col] = 0

    return False

def display_board(board):
    result = ""
    board_size = len(board)

    for i in range(board_size):
        if i % int(board_size**0.5) == 0 and i != 0:
            result += "- " * int((board_size * 1.2 + 1.2)) + "\n"

        for j in range(board_size):
            if j % int(board_size**0.5) == 0 and j != 0:
                result += "| "

            if j == board_size - 1:
                result += str(board[i][j]) + "\n"
            else:
                result += str(board[i][j]) + " "

    return result

def find_empty_cell(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def generate_board(difficulty, board_size):
    def fill_board():
        base = int(board_size ** 0.5)
        side = base * base

        def pattern(r, c): return (base * (r % base) + r // base + c) % side

        def shuffle(s): return random.sample(s, len(s))

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        return [[nums[pattern(r, c)] for c in cols] for r in rows]

    def remove_numbers(board, difficulty):
        squares = side * side
        empties = squares * difficulty // 10
        for p in random.sample(range(squares), empties):
            board[p // side][p % side] = 0

    side = board_size
    board = fill_board()

    while True:
        solved_board = [row[:] for row in board]
        if sudoku_solver(solved_board):
            break
        else:
            board = fill_board()

    remove_numbers(board, difficulty)

    return board, solved_board

def measure_solver_performance(solver_function, board):
    start_time = time.time()
    solved = solver_function(board)
    end_time = time.time()
    
    if solved:
        print(f"Sudoku solved in {end_time - start_time:.4f} seconds.")
    else:
        print("No solution found.")

def user_input(prompt, is_integer=True):
    while True:
        try:
            user_input = input(prompt)
            if is_integer:
                return int(user_input)
            else:
                return user_input
        except ValueError:
            print("Please enter a valid input.")

if __name__ == "__main__":
    difficulty = user_input("Enter difficulty level (1-9): ")
    board_size = user_input("Enter Sudoku board size (4 for 4x4, 9 for 9x9): ")

    generated_board, solution = generate_board(difficulty, board_size)

    print("\nGenerated Sudoku Board: \n")
    print(display_board(generated_board))

    print("\nSudoku Board Solution: \n")
    print(display_board(solution))

    measure_solver_performance(dynamic_parallel_sudoku_solver, generated_board)
