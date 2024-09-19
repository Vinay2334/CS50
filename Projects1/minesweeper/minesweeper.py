import itertools
import random
import copy

N = 8


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=N, width=N, mines=N):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return copy.deepcopy(self.cells)
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return copy.deepcopy(self.cells)
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if len(self.cells) == 0 or cell not in self.cells:
            return
        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if len(self.cells) == 0 or cell not in self.cells:
            return
        self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=N, width=N):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Find Neighbours
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) != cell and (i, j) not in self.moves_made:
                    neighbors.add((i, j))

        new_sentance = Sentence(neighbors, count)
        self.knowledge.append(new_sentance)

        # Empty the known_safe and known_mines sentences
        for sentence in self.knowledge:
            known_safe_set = sentence.known_safes()
            known_mine_set = sentence.known_mines()
            if known_safe_set is not None:
                for cell in known_safe_set:
                    self.mark_safe(cell)
            elif known_mine_set is not None:
                for cell in known_mine_set:
                    self.mark_mine(cell)

         # Filter out empty sentences
        self.knowledge[:] = [
            sentence for sentence in self.knowledge if len(sentence.cells) > 0]

        # Inference based on subsets
        for sentence1, sentence2 in itertools.combinations(self.knowledge, 2):
            if sentence1.cells in sentence2.cells:
                difference_cells = sentence2.cells - sentence1.cells
                difference_count = sentence2.count - sentence1.count
                diff_sentance = Sentence(difference_cells, difference_count)
                # print('subs1', str(sentence2), "Sen", str(
                #     sentence1), "Diff", str(diff_sentance))
                self.handle_inference(diff_sentance)

            elif sentence2.cells in sentence1.cells:
                difference_cells = sentence1.cells - sentence2.cells
                difference_count = sentence1.count - sentence2.count
                diff_sentance = Sentence(difference_cells, difference_count)
                # print('subs2', str(sentence1), "Sen", str(
                #     sentence2), "Diff", str(diff_sentance))
                self.handle_inference(diff_sentance)


        # print([str(sentence) for sentence in self.knowledge])

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return copy.deepcopy(cell)
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = [(i, j) for i in range(self.height) for j in range(self.width)
                           if (i, j) not in self.moves_made and (i, j) not in self.mines]
        if available_moves:
            res = random.choice(available_moves)
            return res
        return None

    def handle_inference(self, inference):
        known_safe_set = inference.known_safes()
        known_mine_set = inference.known_mines()
        if known_safe_set is not None:
            for cell in known_safe_set:
                self.mark_safe(cell)
        elif known_mine_set is not None:
            for cell in known_mine_set:
                self.mark_mine(cell)
        else:
            self.knowledge.append(inference)