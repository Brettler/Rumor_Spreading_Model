import tkinter as tk
from main import spread_rumor
import numpy as np
from tkinter import simpledialog, messagebox
import matplotlib.pyplot as plt
import main as m


class SpreadingRumorsGUI(tk.Tk):
    """
    This class inherits from the 'tk.TK' class, which provides a method to generate an interface for the user,
     and visualizes the spreading rumor model.
    """
    def __init__(self, board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders,
                 rumor_received, flags_board, manual_simulation, num_generations, num_populated_cells,
                 exposed_precentages = 0, cell_size=7):
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
        self.num_generations = num_generations
        self.exposed_percentages = exposed_precentages  # Stores the current percentage of the exposed population.
        self.exposed_population_percentages = []    # List of the percentage of the population that's been exposed.
        self.num_populated_cells = num_populated_cells
        self.doubt_level_percentages = {    # Dictionary of level doubt percentages.
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }
        self.current_iteration = 0  # Initialize the current iteration
        self.results = {    # Results are updated as the simulation progresses.
            "Number of populated cells:": num_populated_cells,
            "Number of generations that passed:": num_generations
        }
        self.iteration_label = tk.Label(self, text=f"Iteration: {self.current_iteration}")  # Display current iteration.
        self.iteration_label.pack()
        # Method from the tkinter package, will generate the grid.
        # This method receives a number of pixels, so we give the dimensions of the grid we want (100*100 in our case),
        # and multiply it by the size of cell. This way the pixels of the cells are taken into account.
        self.canvas = tk.Canvas(self, width=board.shape[1] * cell_size, height=board.shape[0] * cell_size)
        self.canvas.pack()  # visualize the grid in the main window.

        # Checks if the user decided to run the simulation automatically or manually:
        if self.manual_simulation:
            # The manual simulation requires a button to progress the generations.
            self.advance_button = tk.Button(self, text="Advance One Generation", command=self.advance_one_generation)
            self.advance_button.pack()
            self.draw_board()
        else:
            # Updates the visualization with each iteration.
            self.update_canvas()

    def draw_board(self):
        # Clear the board from all the states (= colors), so we can visualize the next generation.
        self.canvas.delete("all")
        # Generate dictionary so each level of doubt will correspond to a color.
        # 4 - not believe,
        # 3 - believe in p=1/3,
        # 2 - believe in 2/3,
        # 1 - believe in everything.
        colors = {-1: "white", 1: "blue", 2: "green", 3: "orange", 4: "red", 5: "pink"}

        # Nested loop iterating over each cell in the grid:
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                color = colors[self.board[row, col]]    # Mapping the level of doubt to the corresponding color.
                # Calculate the pixels positions for the current cell.
                # top-left coordinates:
                left = col * self.cell_size
                top = row * self.cell_size
                # bottom-right coordinates:
                right = (col + 1) * self.cell_size
                bottom = (row + 1) * self.cell_size
                # Calling the method with the arguments above provided by tkinter:
                self.canvas.create_rectangle(left, top, right, bottom, fill=color)

    def advance_one_generation(self):
        # Calling spread_rumor() to calculate the next generation interation.
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board, \
            self.exposed_percentages = spread_rumor(self.board, self.banned_rumor_spreaders, self.L,
                                                    self.original_doubt_lvl_spreaders, self.rumor_received,
                                                    self.flags_board)
        # Increment the iteration number and update the label.
        self.current_iteration += 1
        self.iteration_label.config(text=f"Iteration: {self.current_iteration}")
        # Draw the board of the next generation.
        self.draw_board()

    def update_canvas(self):
        self.draw_board()
        # Calling the method spread_rumor to update the board and the rumor_spreaders
        # (cells who are not allowed to spread a rumor for L generations).
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board, self.exposed_percentages\
            = spread_rumor(self.board, self.banned_rumor_spreaders, self.L, self.original_doubt_lvl_spreaders,
                           self.rumor_received, self.flags_board)
        # Store the percentage of the population that was exposed to a rumor in the current generation.
        self.exposed_population_percentages.append(self.exposed_percentages)
        # Increment the iteration number and update the label.
        self.current_iteration += 1
        self.iteration_label.config(text=f"Iteration: {self.current_iteration}")

        # Run the model the number of generations the user provided recursively:
        if self.current_iteration < self.num_generations:
            # Calculate the percentage of each level of doubt during each iteration for report.
            self.calculate_doubt_level_percentages()
            # Method from tkinter package, updates the canvas after 100 milliseconds.
            # This way the visualization is more responsive and understandable when passing generations.
            self.after(200, self.update_canvas)

        # Finished running the simulation, time to get results:
        if int(self.current_iteration) == int(self.num_generations):
            # Calculate the number of cells that were exposed to a rumor (all cells that are 'true').
            exposed_population = np.sum(self.flags_board)
            self.results["Number of people who received the rumor"] = exposed_population
            self.results["Percentage of people who received the rumor:"] = self.exposed_percentages
            never_exposed = 0
            row, col = self.flags_board.shape
            for i in range(row):
                for j in range(col):
                    if not self.flags_board[i, j] and self.original_doubt_lvl_spreaders[i, j] != -1:
                        never_exposed += 1
            self.results["Number of people who never received the rumor:"] = never_exposed
            never_exposed_percentages = (never_exposed / num_populated_cells) * 100
            rounded_percentage = round(never_exposed_percentages, 3)
            self.results["Percentage of people who never received the rumor"] = rounded_percentage

            # Methods for generating plots:
            self.plot_exposed_population_percentages()
            self.plot_doubt_level_percentages()
            # Display the results in a new dialog window:
            over = tk.Tk()
            over.withdraw()
            results_window = ResultsWindow(over, self.results)
            results_window.grab_set()


    """
    These methods helped us generate the plots needed for our report,
    we kept them in our code if needed to show how the plots were made:
    """
    ###########################################################################################
    ###########################################################################################

    def plot_exposed_population_percentages(self):

        iterations = range(len(self.exposed_population_percentages))
        plt.plot(iterations, self.exposed_population_percentages)
        plt.xlabel("Iterations")
        plt.ylabel("Exposed Population Percentage")
        plt.title("Rumor Spreading Over Time")
        # Save the plot as an image file
        plt.savefig("rumor_spreading_over_time.png", dpi=600)
        plt.show()

    def plot_doubt_level_percentages(self):

        iterations = range(len(self.doubt_level_percentages[1]))
        colors = {1: "blue", 2: "green", 3: "orange", 4: "red", 5: "pink"}
        labels = {
            1: "S1 - Believe everything",
            2: "S2 - Believe with 2/3 probability",
            3: "S3 - Believe with 1/3 probability",
            4: "S4 - Does not believe",
            5: "Rumor spreaders"
        }

        for doubt_level in self.doubt_level_percentages:
            plt.plot(iterations, self.doubt_level_percentages[doubt_level], color=colors[doubt_level],
                     label=labels[doubt_level])

        plt.xlabel("Iterations")
        plt.ylabel("Percentage")
        plt.title("Doubt Level Percentages Over Time")
        plt.legend(loc="best")
        plt.savefig("Doubt_Level_Percentages_Over_Time.png", dpi=600)
        plt.show()

    def calculate_doubt_level_percentages(self):
           total_population = np.sum(self.board != -1)
           for doubt_level in self.doubt_level_percentages.keys():
               count = np.sum(self.board == doubt_level)
               percentage = (count / total_population) * 100
               rounded_percentage = round(percentage, 3)
               self.doubt_level_percentages[doubt_level].append(rounded_percentage)
    ###########################################################################################
    ###########################################################################################


class InitialParametersWindow(simpledialog.Dialog):
    """
    This class inherits from the 'simpledialog.Dialog' class. It provides us with a method that generates an interface
    for the user, so he/she can set the parameters of the model.
    """
    def __init__(self, parent):
        # Set the variable parameters. We will store the setting the user chose later.
        self.parameters = None
        super().__init__(parent)

    def body(self, feature):
        """
        :param feature: Using the parent class to make different features.
        :return: Create the content of the custom dialog window.
        """

        # Set title of the dialog window:
        message1 = "Please enter the parameters for the simulation:"
        message2 = "(Note: The ratio for S4 will be the remaining population," \
                   " Sum of ratio must be equal or less than 1)"
        tk.Label(feature, text=message1).grid(row=0, column=0, columnspan=2)
        tk.Label(feature, text=message2).grid(row=1, column=0, columnspan=2)

        # Set a label for each feature in the dialog window:
        tk.Label(feature, text="Board size:").grid(row=2)
        tk.Label(feature, text="S1 ratio - believe every rumor:").grid(row=3)
        tk.Label(feature, text="S2 ratio - believe a rumor with a 2/3 probability:").grid(row=4)
        tk.Label(feature, text="S3 ratio - believe a rumor with a 1/3 probability:").grid(row=5)
        tk.Label(feature, text="L - The number of generations to wait before spreading a rumor again").grid(row=6)
        tk.Label(feature, text="P - population density:").grid(row=7)
        tk.Label(feature, text="Number of generations:").grid(row=8)

        # Create six features, each corresponding to a parameter that the user will choose:
        self.f1 = tk.Entry(feature)     # Size
        self.f2 = tk.Entry(feature)     # S1 ratio
        self.f3 = tk.Entry(feature)     # S2 Ratio
        self.f4 = tk.Entry(feature)     # S3 Ratio
        self.f5 = tk.Entry(feature)     # L
        self.f6 = tk.Entry(feature)     # P
        self.f7 = tk.Entry(feature)     # Generation

        # Choose the position of each feature in the dialog window:
        self.f1.grid(row=2, column=1)
        self.f2.grid(row=3, column=1)
        self.f3.grid(row=4, column=1)
        self.f4.grid(row=5, column=1)
        self.f5.grid(row=6, column=1)
        self.f6.grid(row=7, column=1)
        self.f7.grid(row=8, column=1)

        # Set default values:
        self.f1.insert(0, "100")
        self.f2.insert(0, "0.25")
        self.f3.insert(0, "0.25")
        self.f4.insert(0, "0.25")
        self.f5.insert(0, "3")
        self.f6.insert(0, "0.6")
        self.f7.insert(0, "100")

        tk.Label(feature, text="Select the initial grid mode:").grid(row=9)
        # Create a dropdown menu to select the type of board:
        self.board_var = tk.StringVar(feature)
        # If the user doesn't change the board settings, they will be set to default.
        self.board_var.set("Classic-Random")
        # Types of boards the user can pick from.   (Three custom boards for part B)
        boards = ["Classic-Random", "Layers", "Half&Half", "Nested Rectangles"]
        self.board_dropdown = tk.OptionMenu(feature, self.board_var, *boards)
        # Location in the window dialog where the selection will be.
        self.board_dropdown.grid(row=9, column=1)

        # Create boolean variable to store the decision of the checkbox (Selected will be true, otherwise false).
        self.manual_simulation_bool = tk.BooleanVar()
        # Create a button in the dialog window using the father class and link the button to the variable we created.
        self.manual_simulation_checkbox = tk.Checkbutton(feature, text="Manual Simulation",
                                                         variable=self.manual_simulation_bool)
        # Set the position of the checkbox.
        self.manual_simulation_checkbox.grid(row=10, column=1)

    def apply(self):
        """
        :return: Initialize The parameters of the simulation with the user choices.
        """
        size = int(self.f1.get())
        s1_ratio = float(self.f2.get())
        s2_ratio = float(self.f3.get())
        s3_ratio = float(self.f4.get())
        L = int(self.f5.get())
        P = float(self.f6.get())
        manual_simulation = self.manual_simulation_bool.get()
        board_choice = self.board_var.get()
        num_generations = int(self.f7.get())
        print(num_generations)
        self.parameters = (size, s1_ratio, s2_ratio, s3_ratio, L, P, manual_simulation, board_choice, num_generations)


class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, results):
        super().__init__(parent)
        self.results = results
        self.title("Spread Rumor Model - Results")

        # Set title for the dialog window
        message = "Spreading Rumors Simulation Results:"
        tk.Label(self, text=message).grid(row=0, column=0, columnspan=2)
        pos = 1
        for k, v in results.items():
            tk.Label(self, text=k).grid(row=pos, column=0)
            result_label = tk.Label(self, text=v)
            result_label.grid(row=pos, column=1)
            pos += 1

        tk.Button(self, text="OK", command=self.destroy).grid(row=pos, columnspan=2)


if __name__ == "__main__":
    # Generate object from the class we inherited.
    root = tk.Tk()
    root.withdraw()
    initial_parameters_window = InitialParametersWindow(root)

    # Store the parameters selected by the user or the default parameters into variables.
    size, s1_ratio, s2_ratio, s3_ratio, L, P, manual_simulation, board_choice, num_generations =\
        initial_parameters_window.parameters
    # Generate the size of the board (Height, Width).
    size = (size, size)
    start_row = 50
    start_col = 50
    board = None
    num_populated_cells = 0

    # Initialize the board chosen by the user with the values of his choice.
    if board_choice == "Classic-Random":
        # Initialize board to classic mode, as requested in part A.
        board, num_populated_cells = m.initialize_board(size, P, s1_ratio, s2_ratio, s3_ratio)

        # Randomly select a person to start spreading the rumor. In order to make sure we select a random person,
        # we made sure to select a populated cell. We will continue to randomly select cells until the
        # cell is != -1 (unpopulated cell).
        while True:
            start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
            if board[start_row, start_col] != -1:
                break

    # Rest of the boards will be deterministic and will answer part B.
    if board_choice == "Layers":
        # We split this board into four parts, each will be filled with different levels of doubt.
        board, num_populated_cells = m.initialize_board_Layers(size, P, s1_ratio, s2_ratio, s3_ratio)
    elif board_choice == "Half&Half":
        # This board will be split in two.
        board, num_populated_cells = m.initialize_board_half_half(size, P, s1_ratio, s2_ratio, s3_ratio)
    elif board_choice == "Nested Rectangles":
        # Initialize board for Board 3.
        board, num_populated_cells = m.initialize_board_nested_rectangles(size, P)

    while True:
        if board[start_row, start_col] != -1:
            break
        else:
            neighbors_list = m.get_neighbors(board, start_row, start_col)
            for r, c in neighbors_list:
                start_row = r
                start_col = c
                if board[start_row, start_col] != -1:
                    break

    # Check if the selected cell has a level of doubt of four.
    if board[start_row, start_col] == 4:
        messagebox.showwarning("Warning", "Oh no! a level S4 square has been selected! The rumor will not spread!")

    # Initialize empty dictionary in the size of the board. When we select a random cell to start the rumor, we will
    # add it to the 'banned_rumor_spreaders' so we can track how many generation it needs to wait until it can
    # spread a rumor again (L generations).
    rumor_spreaders = {}
    # Create a new matrix to track for each generation how many rumors were received.
    rumor_received = np.zeros(board.shape)
    # Create a new board of boolean flags, initialized with False values.
    # This matrix will flag to us if a cell is active and can spread rumor or not.
    flags_board = np.full(size, False, dtype=bool)

    # Select a cell to start spreading the rumor and set it to 'true'.
    flags_board[start_row, start_col] = True
    # Store the original board into a new variable to always remember the innate state of each cell.
    original_doubt_lvl_spreaders = np.copy(board)
    print(f"Chosen type of cell that start rumor: {board[start_row, start_col]}")
    print(f"Coordinates: {start_row}, {start_col}")

    # Create a GUI object with the initialized parameters.
    GUI = SpreadingRumorsGUI(board, rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board,
                             manual_simulation, num_generations, num_populated_cells)
    # Keep the GUI running until the user closes the window.
    GUI.mainloop()
