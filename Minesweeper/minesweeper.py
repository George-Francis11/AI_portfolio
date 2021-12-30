# import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

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


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        if isinstance(other, int):
            return len(self.cells) == other
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if the number of cells equals the number of mines, then all the cells are mines
        if self.count == len(self.cells):
            return self.cells
        # if the count is zero, then return an empty cell of mines
        elif self.count == 0:
            return set()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if the count of mines is zero, then all the cells are safe cells
        if self.count == 0:
            return self.cells
        # if all cells are mines, then there is no safe cells
        elif self.count == len(self.cells):
            return set()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1
        return None

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)
        return None


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

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

    def add_sentence(self, cell, count):
        '''
        This function takes a cell and constructs the sentence from the cells around it
        it iterates over the neighbor cells in the grid while ensuring it does not go out of bounds
        then it checks if any of the neighbor cells is mine it removes it from the new sentence and
        decrements the counter. and if it is a safe cell it just removes it
        :param cell: cell to construct a sentence around it
        :param count: number of mines in the adjacent cells
        :return: None
        '''
        new_sentence = set()
        new_count = count
        curr_x = cell[0]
        curr_y = cell[1]
        for i in range(curr_x - 1, curr_x + 2):
            for j in range(curr_y - 1, curr_y + 2):
                new_cell = (i, j)
                if cell == new_cell:
                    None
                else:
                    if 0 <= new_cell[0] < self.height and 0 <= new_cell[1] < self.width:
                        if new_cell in self.mines:
                            new_count -= 1
                        elif new_cell in self.safes or new_cell in self.moves_made:
                            pass
                        else:
                            new_sentence.add((i, j))
        self.knowledge.append(Sentence(new_sentence, new_count))

    def clean_knowledge(self):

        '''

        This function is a loop that keeps running until it completes one whole iteration without changing anything
        in the knowledge base in each iteration, it checks if there are any known mines or safe cells that still
        exist in sentences. then they need to be removed and update the knowledge base another thing this function
        does, is checking for new sentences. this is done by simplifying for example, if {A,B,C,D} = 2.
        and if {A, C} = 1..... we can simplify the first sentence by removing the sub sentence

        :return: None
        '''

        made_changes = False
        # this loop will keep running unless it executes a whole loop without any changes to the KB
        while True:

            made_changes = False

            safe_cells = set()
            mine_cells = set()

            for sentence1 in self.knowledge:
                for cell in sentence1.known_safes():
                    safe_cells.add(cell)
                for cell in sentence1.known_mines():
                    mine_cells.add(cell)

            if len(safe_cells) != 0:
                made_changes = True
                for c in safe_cells:
                    self.mark_safe(c)
            if len(safe_cells) != 0:
                made_changes = True
                for c in mine_cells:
                    self.mark_mine(c)

            # 5- add any new sentences to the AI's knowledge base
            for sentence1 in self.knowledge:
                if sentence1 == 0:
                    self.knowledge.remove(sentence1)
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 == sentence2:
                        continue
                    if sentence1.cells.issubset(sentence2.cells):
                        different_cells = set()
                        for cell in sentence2.cells:
                            if cell not in sentence1.cells:
                                different_cells.add(cell)
                        temp = Sentence(cells=different_cells, count=sentence2.count - sentence1.count)
                        if temp not in self.knowledge:
                            self.knowledge.append(temp)
                            made_changes = True
            if not made_changes:
                break

    def add_knowledge(self, cell, count):
        '''
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

        :param cell: the cell the agent just visited
        :param count: number of mines in neighbor cells
        :return:  None
        '''
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        # add_knowledge(5,1)  ==> {1,2,3,4,6,7,8,9} = 1
        self.add_sentence(cell, count)
        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        # concluded based on the AI's knowledge base
        # AND
        # 5 add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        self.clean_knowledge()

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
                # return a cell that is safe && not visited
                return cell
        # no safe move possible
        return None

    def make_random_move(self):
        """
            Returns a move to make on the Minesweeper board.
            Should choose randomly among cells that:
                1) have not already been chosen, and
                2) are not known to be mines
            """
        # loops over all the cells in the grid
        possible_cells = []
        for i in range(0, self.height):
            for j in range(0, self.width):
                try_cell = (i, j)
                # if not visited && not mine ==> return it
                if try_cell not in self.moves_made and try_cell not in self.mines:
                    possible_cells.append( try_cell)
        # no possible move at all
        if possible_cells:
            return random.choice(possible_cells)
        return None
