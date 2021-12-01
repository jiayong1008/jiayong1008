# Sudoku
A sudoku solver capable of solving any sudoku problem that is deemed solvable. The program initially tries to deduce new knowledge from given question (in the form of a txt file), when it can't infer anymore new knowledge, it executes a backtracking algorithm to fill in missing values, making sure that it doesn't cause confliction while assigning values. 

## Summarized Implementation of Sudoku Solver
1. Create a `Sudoku` class which takes in a file (sudoku question), and analyze it (know which position of the cell is given in question and which should be filled in).
2. Create a `Variable` class to store all sudoku cells, each variable contains a i & j coordination, its value (if provided in question), and its grid index.
3. Create a `SudokuCreator` keeping track of domains (possible values) of each variable, this class has a `solve` function to solve the sudoku, and a `print` function to print the output of sudoku.

## Summarized Logic of Sudoku Solver
1. Solve beginning from grids. There are 9 grids, choose the grid with the least remaining variable first.
    - For each variable in grid, find its domain by intersecting set of row values, col values, grid values, and its own current domain values.
    - It's domain should be updated to the intersection result if the result is a subset of current domain.
    - If the intersection only has 1 value, congratulations, that's the correct value for that variable.
    - Repeat the above 3 steps until there are no more changes.
    - Next, we find hidden singles within the grid. Hidden singles are the only one of its kind in an entire  grid.
    - Repeat until no more changes.
    - This is followed by finding naked pairs. Naked pairs are two cells in a grid having only the same pair of candidates. All other appearances of the two candidates in the same grid can be eliminated.
    - Again, repeat until no changes.
2. Do the same for row and column as in grid, except there is no need to find intersection between row, col, and grid, since that's already done in step 1. At this point, all inference that can be made from the given question is made. If there is still missing values, proceed to step 3, otherwise, the sudoku is solved.
3. Attempt backtracking algorithm. This is a recursive function, constantly assigning values to a variable if it does not conflict with neighbours. If confliction occurs, it backtracks to the previously assigned value, and select another value for that variable. Repeat until sudoku is solved (if the question is possible to be solved).

## Files and Directories
- `data` - Consists of sudoku questions. You may want to add your own question to test it as well!
- `sudoku.py` - Main program file.
- `README.md` - Describes this project.

## Installation
1. Run `pip install termcolor` if haven't already.
2. Execute `python sudoku.py data/{sudoku-file.txt}`.

## Inspiration and Prep Talk
Inspired by a Crowssword project which I have completed while being guided by a Havard Online Course (CS50AI), so I thought sudoku should be quite similar to it. Little did I know it ate up lots of my brain cells and I thought I was an idiot for taking days to solve it. Anyways, I implemented it bits by bits, debugged it, and completed it. I believe there are improvements that can be made in this program, do let me know if there are, until then, 😆.
