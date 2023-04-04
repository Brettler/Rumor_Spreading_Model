import tkinter as tk
from main import initialize_board, spread_rumor
import numpy as np

class SpreadingRumorsGUI(tk.Tk):
    """
    The class inherits from tk.TK class. It will provide us method to generate interface for the user and visualize
    the spreading rumor model.
    """
    def __init__(self, grid, banned_rumor_spreaders, L, cell_size=10):
        # Calling the parent constructor to generate the main windows for display.
        super().__init__()
        # Initialized the parameters:
        self.board = grid
        self.banned_rumor_spreaders = banned_rumor_spreaders
        self.L = L
        self.cell_size = cell_size
        # Method from tkinter package, will generate the grid.
        # This method receive number of pixel, so we need to take the dim of the grid we want (100*100 in our case)
        # and multiply it by the size of cell. This way the pixels of the cells taking into account also.
        self.canvas = tk.Canvas(self, width=grid.shape[1] * cell_size, height=grid.shape[0] * cell_size)
        # visualize the grid in the main window.
        self.canvas.pack()
        # will keep the visualize updating in each generation.
        self.update_canvas()

    def update_canvas(self):
        """
        :return:
        """

        # Clear the board (from all the states = colors), so we can visualize the next generation.
        self.canvas.delete("all")
        # Generate dictionary so each level of doubt will correspond to a color.
        colors = {0: "white", 1: "blue", 2: "green", 3: "yellow", 4: "red"}

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
        self.board, self.banned_rumor_spreaders = spread_rumor(self.board, self.L, self.banned_rumor_spreaders)
        # Method from tkinter package, updating the canvas after 100 milliseconds. This way we make more
        # responsive and understandable visualization when passing generations.
        self.after(100, self.update_canvas)

if __name__ == "__main__":
    size = (100, 100)
    s1_ratio = 0.25
    s2_ratio = 0.25
    s3_ratio = 0.25
    L = 5
    board = initialize_board(size, s1_ratio, s2_ratio, s3_ratio)

    # Randomly select a person to start spreading the rumor
    rumor_spreaders = np.zeros(size, dtype=np.uint8)
    start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
    rumor_spreaders[start_row, start_col] = L

    app = SpreadingRumorsGUI(board, rumor_spreaders, L)
    app.mainloop()

