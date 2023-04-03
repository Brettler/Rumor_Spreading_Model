import tkinter as tk
from main import initialize_board, spread_rumor
import numpy as np

class SpreadingRumorsGUI(tk.Tk):
    def __init__(self, grid, rumor_spreaders, L, cell_size=10):
        super().__init__()
        self.board = grid
        self.rumor_spreaders = rumor_spreaders
        self.L = L
        self.cell_size = cell_size
        self.canvas = tk.Canvas(self, width=grid.shape[1] * cell_size, height=grid.shape[0] * cell_size)
        self.canvas.pack()
        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        colors = {0: "white", 1: "blue", 2: "green", 3: "yellow", 4: "red"}

        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                color = colors[self.board[row, col]]
                self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                              (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                              fill=color)

        self.board, self.rumor_spreaders = spread_rumor(self.board, self.L, self.rumor_spreaders)
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
