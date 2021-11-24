import sys
from termcolor import cprint


# Cell Variable (Individual Box in Sudoku)
class Variable():
    """Create a new variable with x, y position, and fixed status (True/False)"""
    def __init__(self, i, j, value, grid):
        self.i = i
        self.j = j
        self.value = value
        self.grid = grid

    def __eq__(self, other):
        return (
            (self.i == other.i) and
            (self.j == other.j) and
            (self.value == other.value) and
            (self.grid == other.grid)
        )

    def __hash__(self):
        return hash((self.i, self.j, self.value, self.grid))

    def __str__(self):
        return f"({self.i}, {self.j}), value={self.value}, grid {self.grid}"

    def __repr__(self):
        return f"Variable({self.i}, {self.j}), value={self.value}, grid {self.grid}"


class Sudoku():
    SIZE = 9

    def __init__(self, structure_file):

        # Determine structure of sudoku
        with open(structure_file) as file:
            contents = file.read().splitlines()

        self.variables = set()
        self.structures = []
        for i in range(self.SIZE):
            row = []
            for j in range(self.SIZE):
                value = None if contents[i][j] == '_' else contents[i][j]
                self.variables.add(Variable(
                    i=i,
                    j=j,
                    value=int(value) if value else value,
                    grid=self.get_grid(i, j)
                ))
                row.append(True if value is None else False)
            self.structures.append(row)


    def get_grid(self, i, j):
        """
            Returns grid index given cell position - grids are indexed from 0 to 8 top down, left right
            0 1 2
            3 4 5
            6 7 8
        """
        grids = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        row = int(i / 3)
        col = int(j / 3)
        return grids[row][col]

    # def neighbours(self, var):
    #     """Given a variable, return set of neughbour variables (same row / column / grid)."""
    #     result = set()
    #     for v in self.variables:
    #         if v == var:
    #             continue
    #         if v.i == var.i or v.j == var.j or v.grid == var.grid:
    #             result.add(v)
    #     return result


class SudokuCreator():
    SIZE = 9

    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.domains = dict()
        self.grpdomains = dict()
        possible_values = set(range(1, 10))
        self.answer = [
            [None for _ in range(self.SIZE)]
            for _ in range(self.SIZE)
        ]

        # Possible domains for each row, cell, and grid
        for i in range(self.SIZE):
            for type in ['row', 'col', 'grid']:
                self.grpdomains[f'{type}{i}'] = possible_values.copy()

        for var in self.sudoku.variables:
            value = var.value

            # Empty cell
            if value is None:
                self.domains[var] = possible_values
                continue

            # Remove known value from group domain
            i, j, grid = var.i, var.j, var.grid
            for index, type in zip([i, j, grid], ['row', 'col', 'grid']):
                try:
                    self.grpdomains[f'{type}{index}'].remove(value)
                # This value has been removed previously
                except KeyError:
                    pass
            self.answer[i][j] = value


    def solve(self):
        assignment = dict()
        count= 0
        while True:
            count += 1
            if count == 500:
                print("Looped every grid for 500 times and still no solution.")
                return assignment

            initial = len(assignment)
            for grid in self.select_unassigned_grid():
                revised = True
                while revised:
                    revised_node, assignment = self.enforce_node_consistency(assignment, grid)
                    # If assginment is revised, check if current grid is completed
                    if revised_node and self.grid_complete(grid, assignment):
                        break

                    # Compare values with other variables within the grid to deduce new knowledge
                    revised, assignment = self.enforce_grid_consistency(assignment, grid)
                    if revised and self.grid_complete(grid, assignment):
                        break

                """
                Find Naked pairs
                Two cells in a row, a column, or a block having only the same pair of candidates are called a Naked Pair.
                All other appearances of the two candidates in the same row, column, or block can be eliminated.
                """
            
            """
            Find Hidden Single
            A cell with multiple candidates is called a Hidden Single if one of the candidates is the only 
            candidate in a row, a column, or a block. The single candidate is the solution to the cell. 
            All other appearances of the same candidate, if any, are eliminated if they can be seen by the Single.
            """

            if self.assignment_complete(assignment):
                return assignment
            elif len(assignment) == initial:
                print(f"No more inference can be made. This is the best we can do. Looped {count} times.")
                return assignment


    def enforce_node_consistency(self, assignment, grid):
        """Update domain of cells in grid according to their respective row, column, grid"""
        
        # Initially, revised will be set to True for the sake of entering the while loop for the first time
        initial = len(assignment)
        revised = True        
        count = 0
        gridDomain = self.grpdomains[f'grid{grid}']
        
        while revised:
            count += 1
            if count == 1000:
                raise Exception(f"Unlimited loop in grid {grid}, try debugging")
            revised = False

            # Try to make new inference
            for var in self.get_variables(grid, assignment):
                i, j = var.i, var.j
                rowDomain = self.grpdomains[f'row{i}']
                colDomain = self.grpdomains[f'col{j}']
                conclusion = set.intersection(gridDomain, rowDomain, colDomain)

                # Found answer for this variable
                if len(conclusion) == 1:
                    assignment[var] = conclusion.pop()
                    rowDomain.remove(assignment[var])
                    colDomain.remove(assignment[var])
                    gridDomain.remove(assignment[var])
                    if len(rowDomain) == 0 or len(colDomain) == 0 or len(gridDomain) == 0:
                        break
                    revised = True

                # New inference made
                elif conclusion < self.domains[var]:
                    self.domains[var] = conclusion
                    revised = True

        revised = True if len(assignment) != initial else False
        return revised, assignment


    def enforce_grid_consistency(self, assignment, grid):
        tmp_assignment = dict()
        gridDomain = self.grpdomains[f'grid{grid}']
        for domain in gridDomain:
            for var in self.get_variables(grid, assignment):
                if domain not in self.domains[var]:
                    continue
                if domain in tmp_assignment:
                    del tmp_assignment[domain]
                    break
                else:
                    tmp_assignment[domain] = var
        
        revised = False
        for domain, var in tmp_assignment.items():
            assignment[var] = domain
            self.grpdomains[f'row{var.i}'].remove(domain)
            self.grpdomains[f'col{var.j}'].remove(domain)
            self.grpdomains[f'grid{var.grid}'].remove(domain)
            revised = True
        return revised, assignment


    def select_unassigned_grid(self):
        """Return not fully assigned grid(s) in ascending order"""
        result = dict()
        for i in range(self.SIZE):
            length = len(self.grpdomains[f'grid{i}'])
            if length > 0:
                result[i] = length
        return [val for val, _ in sorted(result.items(), key=lambda item: item[1])]


    def get_variables(self, grid, assignment):
        """Return unassigned variables from a grid"""
        result = set()
        row = int(grid / 3) * 3
        col = (grid % 3) * 3
        for i in range(3):
            for j in range(3):
                if self.sudoku.structures[row+i][col+j]:
                    result.add((row+i, col+j))

        variables = []
        for var in self.domains:
            if (var.i, var.j) in result and var not in assignment:
                variables.append(var)
        return variables


    def assignment_complete(self, assignment):
        """Checks if assignment is completed"""
        for var in self.sudoku.variables:
            if var.value is None and var not in assignment:
                return False
        return True


    def grid_complete(self, grid, assignment):
        """Checks if grid is completed"""
        variables = self.get_variables(grid, assignment)
        return len(variables) == 0


    def print(self, assignment):
        """Print sudoku solution"""
        self.populate_answer(assignment)
        print()
        for i in range(self.SIZE):
            if (i % 3 == 0):
                print("--" * 8)
            for j in range(self.SIZE):
                if (j % 3) == 0 and j != 0:
                    print(" █ ", end='')
                if self.sudoku.structures[i][j]:
                    char = self.answer[i][j] if self.answer[i][j] else '_'
                    cprint(char, 'green', end='')
                else:
                    print(self.answer[i][j], end='')
            print()
        print()

    
    def populate_answer(self, assignment):
        """Populate answer in 2D arrays - Helper function for self.print()"""
        for var, num in assignment.items():
            i, j = var.i, var.j
            # if len(num) != 1:
            #     raise Exception(f"Cell[{i}][{j}] is assigned to more than 1 value.")
            self.answer[i][j] = num
        return


def main():

    # Check usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python sudoku.py structure_file")

    # Parse command-line arguments
    structure = sys.argv[1]

    # Generate sudoku
    sudoku = Sudoku(structure)
    creator = SudokuCreator(sudoku)
    assignment = creator.solve()

    # # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)


if __name__ == "__main__":
    main()
