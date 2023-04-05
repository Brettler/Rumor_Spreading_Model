import tkinter as tk
from main import initialize_board, spread_rumor
import numpy as np

class SpreadingRumorsGUI(tk.Tk):
    """
    The class inherits from tk.TK class. It will provide us method to generate interface for the user and visualize
    the spreading rumor model.
    """
    def __init__(self, board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board, cell_size=10):
        # Calling the parent constructor to generate the main windows for display.
        super().__init__()
        # Initialized the parameters:
        self.board = board
        self.banned_rumor_spreaders = banned_rumor_spreaders
        self.L = L
        self.original_doubt_lvl_spreaders = original_doubt_lvl_spreaders
        self.cell_size = cell_size
        self.rumor_received = rumor_received
        self.flags_board = flags_board
        # Method from tkinter package, will generate the grid.
        # This method receive number of pixel, so we need to take the dim of the grid we want (100*100 in our case)
        # and multiply it by the size of cell. This way the pixels of the cells taking into account also.
        self.canvas = tk.Canvas(self, width=board.shape[1] * cell_size, height=board.shape[0] * cell_size)
        # visualize the grid in the main window.
        self.canvas.pack()
        # will keep the visualize updating in each generation.
        #self.update_canvas()

        self.advance_button = tk.Button(self, text="Advance one generation", command=self.advance_one_generation)
        self.advance_button.pack()

        self.draw_board()

    def draw_board(self):
        colors = {-1: "white", 0: "black", 1: "blue", 2: "green", 3: "yellow", 4: "red", 5: "pink"}

        self.canvas.delete("all")

        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                color = colors[self.board[row, col]]
                left = col * self.cell_size
                top = row * self.cell_size
                right = (col + 1) * self.cell_size
                bottom = (row + 1) * self.cell_size

                self.canvas.create_rectangle(left, top, right, bottom, fill=color)

    def advance_one_generation(self):
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board = spread_rumor(
            self.board, self.banned_rumor_spreaders, self.L, self.original_doubt_lvl_spreaders, self.rumor_received,
            self.flags_board
        )

        self.draw_board()
    """
    def update_canvas(self):

        # Clear the board (from all the states = colors), so we can visualize the next generation.
        self.canvas.delete("all")
        # Generate dictionary so each level of doubt will correspond to a color.
        # 4 - not believe,
        # 3 - believe in p=1/3,
        # 2 - believe in 2/3,
        # 1 - believe in everything.
        colors = {-1: "white", 0: "black", 1: "blue", 2: "green", 3: "yellow", 4: "red", 5: "pink"}

        # Nested loop iterating on each cell in the grid.
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                # Mapping the level of doubt to the corresponding color.
                color = colors[self.board[row, col]]
                # Calculate the pixels position of the current cell.
                # top-left coordinates:
                left = col * self.cell_size
                top = row * self.cell_size
                # bottom-right coordinates:
                right = (col + 1) * self.cell_size
                bottom = (row + 1) * self.cell_size
                # Calling the method with the arguments above provided by tkinter.
                self.canvas.create_rectangle(left, top, right, bottom, fill=color)

        # Calling the method spread_rumor to update the board and
        # the rumor_spreaders (cells who are not allow to spread rumor for L generation).
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board = spread_rumor(self.board,
                                                                                    self.banned_rumor_spreaders,
                                                                                    self.L,
                                                                                    self.original_doubt_lvl_spreaders,
                                                                                    self.rumor_received,
                                                                                    self.flags_board)
        # Method from tkinter package, updating the canvas after 100 milliseconds. This way we make more
        # responsive and understandable visualization when passing generations.
        self.after(100, self.update_canvas)
        """

if __name__ == "__main__":
    size = (100, 100)
    s1_ratio = 0.25
    s2_ratio = 0.25
    s3_ratio = 0.25
    L = 10
    P = 0.7
    # Initialized the board with the parameters.
    board = initialize_board(size, P, s1_ratio, s2_ratio, s3_ratio)
    # Initialized zeros matrix in the size of the board. When we select the random cell to start the rumor we will
    # select this cell in the 'banned_rumor_spreaders' to track how
    # many generation he needs to wait until spread a rumor again (L generations).

    # Create an empty dictionary for rumor spreaders
    rumor_spreaders = {}
    rumor_received = np.zeros(board.shape)
    # Create a new board with boolean flags, initialized with False values.
    # This matrix will flag to us if a cell is active and can spread rumor.
    flags_board = np.full(size, False, dtype=bool)
    # Randomly select a person to start spreading the rumor
    start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
    # Set the random cell to track the number of generation he cant spread a rumor.
    # Key: the indecise for the cell , Value: 0 for start counting the number of generation we are passing until he can
    # spread rumor again (L generation).
    rumor_spreaders[(start_row, start_col)] = 0
    # randomly selected cell that start spreaing the rumor will be true
    flags_board[start_row, start_col] = True
    original_doubt_lvl_spreaders = np.copy(board)
    # Creat an object of gui with the initialized parameters.
    app = SpreadingRumorsGUI(board, rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board)
    # Keep the gui running until the user close the window.
    app.mainloop()

    generations = 100
    """
    for gen in range(generations):

        board, rumor_spreaders = SpreadingRumorsGUI(board, rumor_spreaders, L)
        # Add any visualization or data collection code here.

    """