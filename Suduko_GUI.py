import tkinter as tk
from tkinter import messagebox
import random
from copy import deepcopy
import time

BASE = 3
BOARD_SIZE = 9
DELAY_TIME = 2000


class SudokuSolver:
    @staticmethod
    def solve_sudoku(board):
        def find_empty_cell(board):
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board[i][j] == 0:
                        return i, j
            return None

        empty_cell = find_empty_cell(board)

        if not empty_cell:
            return True
        else:
            row, col = empty_cell

        for num in range(1, BOARD_SIZE + 1):
            if SudokuSolver.valid_move_check(board, num, (row, col)):
                board[row][col] = num

                if SudokuSolver.solve_sudoku(board):
                    return True

                board[row][col] = 0

        return False

    @staticmethod
    def valid_move_check(board, num, pos):
        row, col = pos

        for i in range(BOARD_SIZE):
            if (
                num in board[row]
                or num in set(board[i][col] for i in range(BOARD_SIZE))
                or num in set(
                    board[i][j]
                    for i in range(3 * (row // BASE), 3 * (row // BASE) + BASE)
                    for j in range(3 * (col // BASE), 3 * (col // BASE) + BASE)
                )
            ):
                return False

        return True


class SudokuGUI(tk.Tk):
    def __init__(self, master=None, board_size=9):
        super().__init__(master)
        self.title("Sudoku Solver")
        self.geometry("600x600")
        self.board_size = board_size
        self.board, self.solution = self.generate_board(5, board_size)
        self.user_entries = [
            [
                tk.StringVar(value=str(self.board[i][j]))
                if self.board[i][j] != 0
                else tk.StringVar()
                for j in range(board_size)
            ]
            for i in range(board_size)
        ]

        self.create_widgets()

    def create_widgets(self):
        for i in range(self.board_size):
            self.columnconfigure(i, weight=1)
            self.rowconfigure(i, weight=1)

        self.entries = [
            [
                tk.Entry(
                    self,
                    width=3,
                    font=('Helvetica', 16),
                    textvariable=self.user_entries[i][j],
                    justify='center',
                    state='disabled' if self.board[i][j] != 0 else 'normal',
                    bd=2,
                    relief="solid",
                )
                for j in range(self.board_size)
            ]
            for i in range(self.board_size)
        ]

        for i in range(self.board_size):
            for j in range(self.board_size):
                entry = self.entries[i][j]
                entry.grid(row=i, column=j, ipadx=10, ipady=10, sticky="nsew")

                if j % 3 == 2 and j > 0:
                    entry.grid(padx=(0, 3))
                if i % 3 == 2 and i > 0:
                    entry.grid(pady=(0, 3))

        self.check_button = tk.Button(
            self, text="Check", command=self.check_entries)
        self.check_button.grid(row=self.board_size, column=4,
                               columnspan=1, pady=10, sticky="nsew")

        self.solve_button = tk.Button(
            self, text="Solve", command=self.solve_sudoku)
        self.solve_button.grid(row=self.board_size + 1,
                               column=4, columnspan=1, pady=10, sticky="nsew")

    def generate_board(self, difficulty, board_size):
        def fill_board():
            side = board_size
            base = int(side ** 0.5)
            squares = side * side

            def pattern(r, c):
                return (base * (r % base) + r // base + c) % side

            def shuffle(s):
                return random.sample(s, len(s))

            r_base = range(base)
            rows = [g * base + r for g in shuffle(r_base)
                    for r in shuffle(r_base)]
            cols = [g * base + c for g in shuffle(r_base)
                    for c in shuffle(r_base)]
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
            if SudokuSolver.solve_sudoku(solved_board):
                break
            else:
                board = fill_board()

        remove_numbers(board, difficulty)

        return board, solved_board

    def check_entries(self):
        correct_entries = 0

        for i in range(self.board_size):
            for j in range(self.board_size):
                user_entry = self.user_entries[i][j].get()
                if user_entry:
                    try:
                        user_entry = int(user_entry)
                        if user_entry == self.solution[i][j]:
                            correct_entries += 1
                            self.highlight_wrong_entry(i, j, 'green')
                        else:
                            self.highlight_wrong_entry(i, j, 'red')
                            messagebox.showinfo(
                            "Wrong Entry", "Incorrect entry at row {} column {}".format(i + 1, j + 1))
                    except (ValueError, TypeError):
                        messagebox.showinfo(
                        "Invalid Entry", "Please enter a valid number.")
 
        if correct_entries == self.board_size**2:
            messagebox.showinfo("You Won!", "Sudoku completed successfully.")

    def highlight_wrong_entry(self, row, column, color):
        entry = self.entries[row][column]
        entry.config(bg=color)
        self.after(DELAY_TIME, lambda row=row, column=column: self.reset_entry_color(row, column))

    def reset_entry_color(self, row, column):
        entry = self.entries[row][column]
        entry.config(bg=self.cget('bg'))


    def solve_sudoku(self):
        start_time = time.time()
        solver = SudokuSolver()
        solved_board = deepcopy(self.board)
        if solver.solve_sudoku(solved_board):
            self.update_user_entries(solved_board)
            end_time = time.time()
            solve_time = end_time - start_time
            messagebox.showinfo(
                "Solved!", f"Sudoku solved in {solve_time:.4f} seconds.")
        else:
            messagebox.showinfo(
                "No Solution", "The Sudoku puzzle has no solution.")

    def update_user_entries(self, solved_board):
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.user_entries[i][j].set(str(solved_board[i][j]))


if __name__ == "__main__":
    root = SudokuGUI()
    root.mainloop()
