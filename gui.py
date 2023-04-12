import tkinter as tk
from main import spread_rumor
import numpy as np
from tkinter import simpledialog, messagebox
# Using to draw the plots.
import matplotlib.pyplot as plt
import main as m


class SpreadingRumorsGUI(tk.Tk):
    """
    The class inherits from tk.TK class. It will provide us method to generate interface for the user and visualize
    the spreading rumor model.
    """
    def __init__(self, board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders,
                 rumor_received, flags_board, manual_simulation, num_generations, num_populated_cells,
                 exposed_precentages = 0, cell_size=8):
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
        # Variables to generate graph for analyze:
        self.exposed_percentages = exposed_precentages
        # Generate a list that will sore the percentages of population that expose to a rumor in each iteration.
        self.exposed_population_percentages = []
        self.num_populated_cells = num_populated_cells
        # Generate a dictionary that wil store the percentages of each level of doubt.
        self.doubt_level_percentages = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }
        # Initialize the current iteration
        self.current_iteration = 0
        # The results will keep update as the game progress
        self.results = {
            "Number of cells with population:": num_populated_cells,
            "Number of generations that passed:": num_generations
        }
        # Create a label to display the current iteration
        self.iteration_label = tk.Label(self, text=f"Iteration: {self.current_iteration}")
        self.iteration_label.pack()
        # Method from tkinter package, will generate the grid.
        # This method receive number of pixel, so we need to take the dim of the grid we want (100*100 in our case)
        # and multiply it by the size of cell. This way the pixels of the cells taking into account also.
        self.canvas = tk.Canvas(self, width=board.shape[1] * cell_size, height=board.shape[0] * cell_size)
        # visualize the grid in the main window.
        self.canvas.pack()

        # Checking if the user decide to run the simulation automatically or manually
        if self.manual_simulation:
            # The simulation run manually will need a button that each time it pressed it the pass generation.
            self.advance_button = tk.Button(self, text="Advance One Generation", command=self.advance_one_generation)
            self.advance_button.pack()
            self.draw_board()
        else:
            # will keep the visualize updating in each generation.
            self.update_canvas()

    def draw_board(self):
        # Clear the board (from all the states = colors), so we can visualize the next generation.
        self.canvas.delete("all")
        # Generate dictionary so each level of doubt will correspond to a color.
        # 4 - not believe,
        # 3 - believe in p=1/3,
        # 2 - believe in 2/3,
        # 1 - believe in everything.
        colors = {-1: "white", 1: "blue", 2: "green", 3: "orange", 4: "red", 5: "pink"}

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

    def advance_one_generation(self):
        # Calling spread_rumor() to calculate the next generation interation.
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board, \
            self.exposed_percentages = spread_rumor(self.board, self.banned_rumor_spreaders, self.L,
                                                    self.original_doubt_lvl_spreaders, self.rumor_received,
                                                    self.flags_board)
        # Increment the iteration number and update the label
        self.current_iteration += 1
        self.iteration_label.config(text=f"Iteration: {self.current_iteration}")
        # Draw the board of the next generation.
        self.draw_board()

    def update_canvas(self):
        self.draw_board()
        # Calling the method spread_rumor to update the board and
        # the rumor_spreaders (cells who are not allow to spread rumor for L generation).
        self.board, self.banned_rumor_spreaders, self.rumor_received, self.flags_board, self.exposed_percentages\
            = spread_rumor(self.board, self.banned_rumor_spreaders, self.L, self.original_doubt_lvl_spreaders,
                           self.rumor_received, self.flags_board)
        # Store the percentage of population that expose to a rumor in a current generation.
        self.exposed_population_percentages.append(self.exposed_percentages)
        # Increment the iteration number and update the label
        self.current_iteration += 1
        self.iteration_label.config(text=f"Iteration: {self.current_iteration}")
        # Running the simulation until 100 iteration:

        if self.current_iteration < self.num_generations:
            # Calculate the percentage of each doubt of level for each iteration to make meaningful
            # figures to our report.
            self.calculate_doubt_level_percentages()
            # Method from tkinter package, updating the canvas after 100 milliseconds. This way we make more
            # responsive and understandable visualization when passing generations.
            self.after(200, self.update_canvas)

        # Finished running the simulation and its time for results:
        if int(self.current_iteration) == int(self.num_generations):
            # Calcualte the number of cells that exposed to a rumor (all cells that are true exposed)
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
            self.results["Percentage of people who never received the rumor"] = never_exposed_percentages
            # Calling the methods to generate the plot needed for our report:
            self.plot_exposed_population_percentages()
            self.plot_doubt_level_percentages()
            # Display the results in a new dialog window
            over = tk.Tk()
            over.withdraw()
            results_window = ResultsWindow(over, self.results)
            results_window.grab_set()




    """
    Those methods helped us generated the plots needed for our report,
    we kept them in our code if needed to show how the polts made:
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
            self.doubt_level_percentages[doubt_level].append(percentage)
    ###########################################################################################
    ###########################################################################################


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
        message1 = "Please enter the parameters for the simulation:"
        message2 = "(Note: The ratio for S4 will be the remaining population," \
                   " Sum of ratio must be equal or less than 1)"
        tk.Label(feature, text=message1).grid(row=0, column=0, columnspan=2)
        tk.Label(feature, text=message2).grid(row=1, column=0, columnspan=2)

        # Set label for each feature in the dialog window
        tk.Label(feature, text="Board size (This value sets the height and width of the grid):").grid(row=2)
        tk.Label(feature, text="S1 ratio (The proportion of people who will believe every rumor they hear):").grid(row=3)
        tk.Label(feature, text="S2 ratio (The proportion of people who will believe a rumor with a 2/3 probability):").grid(row=4)
        tk.Label(feature, text="S3 ratio (The proportion of people who will believe a rumor with a 1/3 probability):").grid(row=5)
        tk.Label(feature, text="L (The number of generations a person must wait before spreading a rumor again)").grid(row=6)
        tk.Label(feature, text="P (The overall density of the population):").grid(row=7)
        tk.Label(feature, text="Number of generations:").grid(row=8)

        # Create 6 features, each corresponding to a parameter that the user will choose.
        # Size
        self.f1 = tk.Entry(feature)
        # S1 ratio
        self.f2 = tk.Entry(feature)
        # S2 Ratio
        self.f3 = tk.Entry(feature)
        # S3 Ratio
        self.f4 = tk.Entry(feature)
        # L
        self.f5 = tk.Entry(feature)
        # P
        self.f6 = tk.Entry(feature)
        # Generation
        self.f7 = tk.Entry(feature)

        # Choose the position of each feature in the dialog window.
        self.f1.grid(row=2, column=1)
        self.f2.grid(row=3, column=1)
        self.f3.grid(row=4, column=1)
        self.f4.grid(row=5, column=1)
        self.f5.grid(row=6, column=1)
        self.f6.grid(row=7, column=1)
        self.f7.grid(row=8, column=1)


        # Set default values
        self.f1.insert(0, "100")
        self.f2.insert(0, "0.25")
        self.f3.insert(0, "0.25")
        self.f4.insert(0, "0.25")
        self.f5.insert(0, "3")
        self.f6.insert(0, "0.6")
        self.f7.insert(0, "100")


        tk.Label(feature, text="Select the initial grid mode:").grid(row=9)
        # Create dropdown menu to select the board
        self.board_var = tk.StringVar(feature)
        # If the user don't change the bard setting, it will be set as default.
        self.board_var.set("Classic-Random")
        # Boards that the user can choose between them. (3 costume boards for question B)
        boards = ["Classic-Random", "Layers", "Half&Half", "Nested Rectangles"]
        self.board_dropdown = tk.OptionMenu(feature, self.board_var, *boards)
        # Location in the window dialog where the selection will be.
        self.board_dropdown.grid(row=9, column=1)


        # Create boolean variable to store the decision of the checkbox (Selected will be true, else false).
        self.manual_simulation_bool = tk.BooleanVar()
        # Creat the button in the dialog window using the father class and link the button to the variable we created.
        self.manual_simulation_checkbox = tk.Checkbutton(feature, text="Manual Simulation",
                                                         variable=self.manual_simulation_bool)
        # Set the position of the checkbox.
        self.manual_simulation_checkbox.grid(row=10, column=1)

    def apply(self):
        """
        :return: Initialized The parameters of the simulation with the user choice.
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
    # Generate object from the class we inherence.
    root = tk.Tk()
    root.withdraw()
    initial_parameters_window = InitialParametersWindow(root)

    # Store the parameters selected by the user or the default parameters into variables.
    size, s1_ratio, s2_ratio, s3_ratio, L, P, manual_simulation, board_choice, num_generations =\
        initial_parameters_window.parameters
    # Generate the size of the board (Height, Width)
    size = (size, size)
    start_row = None
    start_col = None
    board = None
    num_populated_cells = 0

    # Initialized the board chosen by the user with the parameters of his chosen.
    if board_choice == "Classic-Random":
        # Initialize board for classic mode. as requested in question A.
        board, num_populated_cells = m.initialize_board(size, P, s1_ratio, s2_ratio, s3_ratio)

        # Randomly select a person to start spreading the rumor. In order to make sure we select a random person
        # meaning we need to make sure we select populate cell. we will keep try to randomly select
        # cells until the cell is != -1 (unpopulated cell)
        while True:
            start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
            if board[start_row, start_col] != -1:
                break
    else:
        start_row = 50
        start_col = 50
    # Rest of the boards will be deterministic and will answer question B.
    if board_choice == "Layers":
        # In this board we split the board to 4 parts, each part will be fill with different level of doubt.
        board = m.initialize_board_Layers(size, P, s1_ratio, s2_ratio, s3_ratio)
    elif board_choice == "Half&Half":
        # This board will be split to
        board = m.initialize_board_half_half(size, s1_ratio, s2_ratio, s3_ratio)
    elif board_choice == "Nested Rectangles":
        # Initialize board for Board 3
        board = m.initialize_board_nested_rectangles(size)

    # Check if the selected cell has a level of doubt of 4
    if board[start_row, start_col] == 4:
        messagebox.showwarning("Warning", "Oh no! a level S4 square has been selected! The rumor will not spread!")

    # Initialized empty dictionary in the size of the board. When we select the random cell to start the rumor we will
    # select this cell in the 'banned_rumor_spreaders' to track how
    # many generation he needs to wait until spread a rumor again (L generations).
    rumor_spreaders = {}
    # Create new matrix that will track for each generation how many rumors he received.
    rumor_received = np.zeros(board.shape)
    # Create a new board with boolean flags, initialized with False values.
    # This matrix will flag to us if a cell is active and can spread rumor.
    flags_board = np.full(size, False, dtype=bool)

    # Selected cell that start spreaing the rumor will be true
    flags_board[start_row, start_col] = True
    # Store the original board into a new variable to always remember the innate state of each cell
    original_doubt_lvl_spreaders = np.copy(board)
    print(f"Chosen type of cell that start rumor: {board[start_row, start_col]}")

    # Creat an object of gui with the initialized parameters.
    GUI = SpreadingRumorsGUI(board, rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board,
                             manual_simulation, num_generations, num_populated_cells)
    # Keep the gui running until the user close the window.
    GUI.mainloop()


