import tkinter as tk
from main import initialize_board, spread_rumor
import numpy as np
from tkinter import simpledialog


class SpreadingRumorsGUI(tk.Tk):
    """
    The class inherits from tk.TK class. It will provide us method to generate interface for the user and visualize
    the spreading rumor model.
    """
    def __init__(self, board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders,
                 rumor_received, flags_board, manual_simulation, cell_size=10):
        # Calling the parent constructor to generate the main windows for display.
        super().__init__()
        self.title("Spreading Rumors Model")
        # Initialized the parameters:
        self.board = board
        self.banned_rumor_spreaders = banned_rumor_spreaders
        self.L = L
        self.original_doubt_lvl_spreaders = original_doubt_lvl_spreaders
        self.cell_size = cell_size
        self.rumor_received = rumor_received
        self.flags_board = flags_board
        self.manual_simulation = manual_simulation
        # Method from tkinter package, will generate the grid.
        # This method receive number of pixel, so we need to take the dim of the grid we want (100*100 in our case)
        # and multiply it by the size of cell. This way the pixels of the cells taking into account also.
        self.canvas = tk.Canvas(self, width=board.shape[1] * cell_size, height=board.shape[0] * cell_size)
        # visualize the grid in the main window.
        self.canvas.pack()
        # will keep the visualize updating in each generation.
        #self.update_canvas()

        if self.manual_simulation:
            self.advance_button = tk.Button(self, text="Advance One Generation", command=self.advance_one_generation)
            self.advance_button.pack()
            self.draw_board()
        else:
            self.update_canvas()

    def draw_board(self):
        colors = {-1: "white", 0: "black", 1: "blue", 2: "green", 3: "yellow", 4: "red", 5: "pink"}

        self.canvas.delete("all")
        print("After we did - > self.canvas.delete(all)")
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                color = colors[self.board[row, col]]
                left = col * self.cell_size
                top = row * self.cell_size
                right = (col + 1) * self.cell_size
                bottom = (row + 1) * self.cell_size

                self.canvas.create_rectangle(left, top, right, bottom, fill=color)

    def advance_one_generation(self):
        print("advance_one_generation")
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board = spread_rumor(
            self.board, self.banned_rumor_spreaders, self.L, self.original_doubt_lvl_spreaders, self.rumor_received,
            self.flags_board
        )
        print("self.draw_board()")
        self.draw_board()

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


class InitialParametersWindow(simpledialog.Dialog):
    """
    The class inherits from simpledialog.Dialog class. It will provide us method to generate interface for the user to
    set the parameters of the model.
    """
    def __init__(self, parent):
        # Set the variable parameters, we will store later the setting of the user choose.
        self.parameters = None
        super().__init__(parent)

    def body(self, feature):
        """
        :param feature: Using the parent class to make different features.
        :return: Create the content of the custom dialog window
        """

        # Set title for the dialog window
        message = "Please enter the parameters for the simulation: " \
                  "(Note: The ratio for S4 will be the remaining population)"
        tk.Label(feature, text=message).grid(row=0, column=0, columnspan=2)

        # Set label for each feature in the dialog window
        tk.Label(feature, text="Board size (This value sets the height and width of the grid):").grid(row=1)
        tk.Label(feature, text="S1 ratio (The proportion of people who will believe every rumor they hear):").grid(row=2)
        tk.Label(feature, text="S2 ratio (The proportion of people who will believe a rumor with a 2/3 probability):").grid(row=3)
        tk.Label(feature, text="S3 ratio (The proportion of people who will believe a rumor with a 1/3 probability):").grid(row=4)
        tk.Label(feature, text="L (The number of generations a person must wait before spreading a rumor again)").grid(row=5)
        tk.Label(feature, text="P (The overall density of the population):").grid(row=6)

        # Create 6 features, each corresponding to a parameter that the user will choose.
        self.e1 = tk.Entry(feature)
        self.e2 = tk.Entry(feature)
        self.e3 = tk.Entry(feature)
        self.e4 = tk.Entry(feature)
        self.e5 = tk.Entry(feature)
        self.e6 = tk.Entry(feature)

        # Choose the position of each feature in the dialog window.
        self.e1.grid(row=1, column=1)
        self.e2.grid(row=2, column=1)
        self.e3.grid(row=3, column=1)
        self.e4.grid(row=4, column=1)
        self.e5.grid(row=5, column=1)
        self.e6.grid(row=6, column=1)

        # Set default values
        self.e1.insert(0, "100")
        self.e2.insert(0, "0.25")
        self.e3.insert(0, "0.25")
        self.e4.insert(0, "0.25")
        self.e5.insert(0, "10")
        self.e6.insert(0, "0.7")

        # Create boolean variable to store the decision of the checkbox (Selected will be true, else false).
        self.manual_simulation_var = tk.BooleanVar()
        # Creat the button in the dialog window using the father class and link the button to the variable we created.
        self.manual_simulation_checkbox = tk.Checkbutton(feature, text="Manual Simulation",
                                                       variable=self.manual_simulation_var)
        # Set the position of the checkbox.
        self.manual_simulation_checkbox.grid(row=7, column=1)


    def apply(self):
        size = int(self.e1.get())
        s1_ratio = float(self.e2.get())
        s2_ratio = float(self.e3.get())
        s3_ratio = float(self.e4.get())
        L = int(self.e5.get())
        P = float(self.e6.get())
        manual_simulation = self.manual_simulation_var.get()

        self.parameters = (size, s1_ratio, s2_ratio, s3_ratio, L, P, manual_simulation)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    initial_parameters_window = InitialParametersWindow(root)
    size, s1_ratio, s2_ratio, s3_ratio, L, P, manual_simulation = initial_parameters_window.parameters
    size = (size, size)
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
    # Randomly select a person to start spreading the rumor. In order to make sure we select a random person
    # meaning we need to make sure we select populate cell. we will keep try to randomly select
    # cells until the cell is != -1 (unpopulated cell)
    while True:
        start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
        if board[start_row, start_col] != -1:
            break

    # randomly selected cell that start spreaing the rumor will be true
    flags_board[start_row, start_col] = True
    original_doubt_lvl_spreaders = np.copy(board)
    # Creat an object of gui with the initialized parameters.
    app = SpreadingRumorsGUI(board, rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board, manual_simulation)
    # Keep the gui running until the user close the window.
    app.mainloop()
