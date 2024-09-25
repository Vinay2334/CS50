import sys
from crossword import *
from collections import defaultdict
import copy


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.
        """
        for var in self.domains:
            words_to_remove = {word for word in self.domains[var] if var.length != len(word)}
            self.domains[var].difference_update(words_to_remove)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        Remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`, else False.
        """
        overlap = self.crossword.overlaps[(x, y)]
        revised = False

        if overlap is None:
            return revised

        x_domain = self.domains[x].copy()
        words_to_remove = set()

        for x_word in x_domain:
            is_consistent = any(
                x_word[overlap[0]] == y_word[overlap[1]] 
                for y_word in self.domains[y]
            )
            if not is_consistent:
                words_to_remove.add(x_word)
                revised = True

        self.domains[x].difference_update(words_to_remove)
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with the initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty.
        Return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = [(x, y) for x in self.crossword.variables for y in self.crossword.neighbors(x)]
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return set(assignment.keys()) == set(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = set()
        for var, word in assignment.items():
            if var.length != len(word) or word in values:
                return False
            values.add(word)

        for var1 in assignment:
            for var2 in self.crossword.neighbors(var1):
                if var2 not in assignment:
                    continue
                overlap = self.crossword.overlaps.get((var1, var2))
                if overlap:
                    i, j = overlap
                    if assignment[var1][i] != assignment[var2][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, ordered by the number of
        values they rule out for neighboring variables.
        """
        neighbors = self.crossword.neighbors(var) - assignment.keys()
        constraint = defaultdict(int)

        for value in self.domains[var]:
            for neighbor in neighbors:
                overlap = self.crossword.overlaps.get((var, neighbor))
                if not overlap:
                    continue
                i, j = overlap
                for neighbor_value in self.domains[neighbor]:
                    if value[i] != neighbor_value[j]: 
                        constraint[value] += 1

        return sorted(self.domains[var], key=lambda value: constraint[value])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not yet in `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest degree.
        """
        unassigned_vars = [var for var in self.crossword.variables if var not in assignment]
        return min(unassigned_vars, key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible.
        Return None if no assignment is possible.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result:
                    return result

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()