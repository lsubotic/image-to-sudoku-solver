from termcolor import colored
import numpy as np
# Other
from recognize_numbers import form_sudoku_grid


def find_empty(grid):
    """
    Find an empty square in the grid and returns its position, if no empty squares are found return None
    """
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j

    return None


def check_position(grid, num, row, col):
    """
    Based on rules, checks if the given 'num' is in a valid position.
    """
    def box_pos(val):
        # Determine coordinates of 3x3 box corresponding to val(row or col of the current square)
        if val < 3:
            pos = 0
        elif 3 <= val < 6:
            pos = 3
        else:
            pos = 6
        return pos

    # Check row
    if num in grid[row, :]:
        return False
    # Check column
    if num in grid[:, col]:
        return False

    # Check box
    pos_y = box_pos(row)
    pos_x = box_pos(col)
    if num in grid[pos_y:pos_y+3, pos_x:pos_x+3]:
        return False

    return True


def solve(grid):
    """
    Solve sudoku using backtracking
    """
    empty_pos = find_empty(grid)
    if not empty_pos:
        # No empty squares, sudoku is solved :)
        return True

    row, col = empty_pos
    for i in range(1, 10):
        # Check if number is valid
        if check_position(grid, i, row, col):
            grid[row][col] = i
            # Recursion until solve is True
            if solve(grid):
                return True

            grid[row][col] = 0
    return False


def print_grid(grid):
    """
    Prints the sudoku grid array in a nicer format
    """
    for i in range(len(grid)):
        if i % 3 == 0 and i != 0:
            print(colored('-------+--------+------', 'blue'))
        for j in range(len(grid[0])):
            if j % 3 == 0 and j != 0:
                print(colored(' | ', 'blue'), end='')
            if j == 8:
                print(grid[i][j])
            else:
                print(str(grid[i][j]) + ' ', end='')


if __name__ == '__main__':
    # Getting the sudoku grid from module as np.array()
    sudoku_grid = np.array(form_sudoku_grid())

    print("Here's the sudoku on image:")
    print_grid(sudoku_grid)
    print()
    solve(sudoku_grid)
    print("And this is the solution :)")
    print_grid(sudoku_grid)







