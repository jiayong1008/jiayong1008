import sys
from termcolor import cprint


# Cell Variable (Individual Cell in Sudoku)
class Variable():
    """Create a new sudoku variable with cell coordinates, i and j, 
        it's value (if provided in question), and grid value (0 to 8)"""

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
            Returns grid index given cell position,
            grids are indexed from 0 to 8 top down, left right:
            0 1 2
            3 4 5
            6 7 8
        """
        grids = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        row = int(i / 3)
        col = int(j / 3)
        return grids[row][col]

    def neighbours(self, assignment, var):
        """Given a variable, return set of unassigned neighbouring variables."""
        results = set()
        for v in self.variables:
            if v == var or v.value is not None or v in assignment:
                continue
            elif v.i == var.i or v.j == var.j or v.grid == var.grid:
                results.add(v)
        return results


class SudokuCreator():
    SIZE = 9

    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.domains = dict()
        # grp domain referring to a specific row, col, or grid
        self.grpdomains = dict()
        possible_values = set(range(1, 10))
        # answer to assist printing upon completion
        self.answer = [
            [None for _ in range(self.SIZE)]
            for _ in range(self.SIZE)
        ]

        # Possible domains for each row, cell, and grid
        for i in range(self.SIZE):
            for type in ['row', 'col', 'grid']:
                self.grpdomains[f'{type}{i}'] = possible_values.copy()

        # Possible domains for empty cell
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
    
    def populate_answer(self, assignment):
        """Populate answer in 2D arrays - Helper function for self.print()"""
        for var, num in assignment.items():
            i, j = var.i, var.j
            self.answer[i][j] = num
        return

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


    def solve(self):
        """Solve the sudoku problem"""
        # assignment maps variable (sudoku cell) to a value, basically the temporary 'answer'
        assignment = dict()
        
        count= 0
        while True:
            count += 1
            if count == 200:
                print("Looped every grid for 200 times and still no solution.")
                return assignment

            # Solve sudoku beginning with grids, then proceed to row and column
            updated_grid = self.solve_grid(assignment)
            updated_row_col = self.solve_row_col(assignment)
            updated = updated_grid or updated_row_col

            if self.assignment_complete(assignment):
                print(f"\nLooped {count} times.")
                return assignment
            # If no more inference can be made from grid, row, and col, execute backtrack algorithm to solve it
            elif not updated:
                print(f"\nNo more inference can be made after {count} loops, attempting backtrack...")
                new_assignment = self.backtrack(assignment)
                if new_assignment:
                    assignment = new_assignment
                else:
                    print("Backtrack failed.")
                return assignment

    def solve_grid(self, assignment):
        updated = False
        for grid in self.select_unassigned_grid():
            revised = True
            while revised:
                # Maintain node and grid consitency
                revised, assignment = self.enforce_grid_consistency(assignment, grid)
                if not revised:
                    break

                updated = True
                revised, assignment = self.find_naked_pairs(assignment, 'grid', grid)

                if self.grid_complete(grid, assignment):
                    break
        return updated

    def solve_row_col(self, assignment):
        """Compare values with other variables within the row and col to deduce new knowledge"""
        updated = False
        while True:
            modified = False
            for i in range(self.SIZE):
                revised_row, assignment = self.find_hidden_single(assignment, 'row', i)
                revised_col, assignment = self.find_hidden_single(assignment, 'col', i)
                if revised_row or revised_col:
                    modified = True

            if not modified:
                break
            updated = True

            for i in range(self.SIZE):
                revised_row, assignment = self.find_naked_pairs(assignment, 'row', i)
                revised_col, assignment = self.find_naked_pairs(assignment, 'col', i)
                if revised_row or revised_col:
                    modified = True

            if not modified:
                break
        return updated

    def enforce_grid_consistency(self, assignment, grid):
        revised = True
        updated = False
        while revised:
            revised_node, assignment = self.enforce_group_consistency(assignment, 'grid', grid)
            # If assginment is revised, check if current grid is completed
            if revised_node:
                updated = True
                if self.grid_complete(grid, assignment):
                    break

            # Compare values with other variables within the grid to deduce new knowledge
            revised, assignment = self.find_hidden_single(assignment, 'grid', grid)
            if revised:
                updated = True
                if self.grid_complete(grid, assignment):
                    break

            revised = revised_node or revised

        return updated, assignment


    def enforce_group_consistency(self, assignment, type, index):
        """Update domain of cells in grid according to their respective row, column, grid"""
        
        # Initially, revised will be set to True for the sake of entering the while loop for the first time
        revised = True
        updated = False        
        count = 0
        grpDomain = dict()
        grpDomain[0] = self.grpdomains[f'{type}{index}']
        
        while revised:
            count += 1
            if count == 200:
                raise Exception(f"Unlimited loop in {type} {index}, try debugging")
            revised = False

            # Try to make new inference
            for var in self.get_variables(assignment, type, index):
                count = 0
                for innerType in ['row', 'col', 'grid']:
                    if innerType == type:
                        continue
                    elif innerType == 'row':
                        value = var.i
                    elif innerType == 'col':
                        value = var.j
                    else:
                        value = var.grid
                    count += 1
                    grpDomain[count] = self.grpdomains[f'{innerType}{value}']
                conclusion = set.intersection(grpDomain[0], grpDomain[1], grpDomain[2], self.domains[var])

                # Found answer for this variable
                if len(conclusion) == 1:
                    assignment[var] = conclusion.pop()
                    self.domains[var] = assignment[var]
                    for i in range(3):
                        grpDomain[i].remove(assignment[var])
                    revised = True
                    updated = True
                    if len(grpDomain[0]) == 0:
                        break

                # Will only come to this case during backtrack function
                # elif len(conclusion) == 0:
                #     return None

                # New inference made
                elif conclusion < self.domains[var]:
                    self.domains[var] = conclusion
                    revised = True
                    updated = True

        return updated, assignment


    def find_hidden_single(self, assignment, type, index):
        """The only one of its kind in an entire row, column, or grid."""
        tmp_assignment = dict()
        grpDomain = self.grpdomains[f'{type}{index}']
        for domain in grpDomain:
            for var in self.get_variables(assignment, type, index):
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
            self.domains[var] = {domain}
            self.update_domain(var, domain)
            revised = True
        return revised, assignment


    def find_naked_pairs(self, assignment, type, index):
        """
        Two cells in a row, a column, or a block having only the same pair of candidates 
        are called a Naked Pair. All other appearances of the two candidates in the same 
        row, column, or block can be eliminated.
        """
        count = 0
        revised = True
        while revised:
            pair_domain = dict()
            real_pair_domain = dict()
            grpVariables = self.get_variables(assignment, type, index)
            for var in grpVariables:
                domain = self.domains[var]
                if len(domain) != 2:
                    continue

                for pair_var, pair in pair_domain.items():
                    if pair == domain:
                        key = (pair_var, var)
                        real_pair_domain[key] = domain
                        break
                if domain not in pair_domain.values():
                    pair_domain[var] = domain
            
            revised = False
            for vars, domain in real_pair_domain.items():
                # If it is row, update entire row, same goes to col
                for grpVar in grpVariables:
                    # Skip the same variable
                    if grpVar in vars:
                        continue
                    for val in domain:
                        try:
                            self.domains[grpVar].remove(val)
                            revised = True
                            count += 1
                        except:
                            pass

        revised = count > 0
        return revised, assignment
    

    def update_domain(self, var, value, add=False):
        """Update domain by adding or removing value"""
        if not add:
            try:
                self.grpdomains[f'row{var.i}'].remove(value)
            except:
                return False

            try:
                self.grpdomains[f'col{var.j}'].remove(value)
            except:
                self.grpdomains[f'row{var.i}'].add(value)
                return False

            try:
                self.grpdomains[f'grid{var.grid}'].remove(value)
            except:
                self.grpdomains[f'row{var.i}'].add(value)
                self.grpdomains[f'col{var.j}'].add(value)
                return False

        else:
            self.grpdomains[f'row{var.i}'].add(value)
            self.grpdomains[f'col{var.j}'].add(value)
            self.grpdomains[f'grid{var.grid}'].add(value)
        return True


    def select_unassigned_grid(self):
        """Return not fully assigned grid(s) in ascending order"""
        result = dict()
        for i in range(self.SIZE):
            length = len(self.grpdomains[f'grid{i}'])
            if length > 0:
                result[i] = length
        return [val for val, _ in sorted(result.items(), key=lambda item: item[1])]


    def get_variables(self, assignment, type, value):
        """Return unassigned variables from a row, col, or grid"""
        result = set()

        if type == 'grid':
            row = int(value / 3) * 3
            col = (value % 3) * 3
            for i in range(3):
                for j in range(3):
                    if self.sudoku.structures[row+i][col+j]:
                        result.add((row+i, col+j))
        elif type == 'row':
            for i in range(self.SIZE):
                result.add((value, i))
        else: # col
            for i in range(self.SIZE):
                result.add((i, value))

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
        variables = self.get_variables(assignment, 'grid', grid)
        return len(variables) == 0

    def select_grid_var(self, assignment, grid):
        vars = self.get_variables(assignment, 'grid', grid)
        return [var for var in sorted(vars, key=lambda var: len(self.domains[var]))]

    def consistent(self, assignment, var, val):
        neighbours = self.sudoku.neighbours(assignment, var)
        for neighbour in neighbours:
            if self.domains[neighbour] == {val}:
                return False
        return True
    
    def order_domain_values(self, assignment, var):
        constraints = dict()
        neighbours = self.sudoku.neighbours(assignment, var)
        for val in self.domains[var]:
            num_constraints = 0
            for neighbour in neighbours:
                if val in self.domains[neighbour]:
                    num_constraints += 1
            constraints[val] = num_constraints

        ordered = [val for val, _ in sorted(constraints.items(), key=lambda x: x[1])]
        return ordered

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        sudoku and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to domains (values).

        If no assignment is possible, return initial assignment.
        """
        if self.assignment_complete(assignment):
            return assignment

        grid = self.select_unassigned_grid()[0]
        var = self.select_grid_var(assignment, grid)[0]
        for val in self.order_domain_values(assignment, var):
            if not self.consistent(assignment, var, val):
                continue
            assignment[var] = val
            succeed = self.update_domain(var, val)
            if not succeed:
                del assignment[var]
                continue
            result = self.backtrack(assignment)
            if result is not None:
                return result
            del assignment[var]
            self.update_domain(var, val, add=True)
        return None
        

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

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)


if __name__ == "__main__":
    main()
