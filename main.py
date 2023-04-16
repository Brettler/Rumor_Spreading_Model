import numpy as np


def initialize_board(size, P, s1_ratio, s2_ratio, s3_ratio):
    """
    :param size: This value sets the height and width of the grid.
    :param P: The overall density of the population.
    :param s1_ratio: The proportion of people who will believe every rumor they hear.
    :param s2_ratio: The proportion of people who will believe a rumor with a 2/3 probability.
    :param s3_ratio: The proportion of people who will believe a rumor with a 1/3 probability.
    :return: Initialized board with each cell's level of doubt.
            Also return the number of cells that are populated.
    """
    rows, cols = size           # Unpack the dimensions of the grid.
    board = np.full(size, -1)   # Initialize an empty board with -1 in all cells.
    total_cells = rows * cols   # Calculate the number of cells.
    num_populated_cells = int(total_cells * P)  # Calculate the number of populated cells based on population density P.

    # Create an array the size of the number of populated cells.
    # Fill this array with the indexes corresponding the cells and then shuffle it.
    populated_cells_idx = np.random.permutation(total_cells)[:num_populated_cells]

    # Calculate the number of cells for each level of doubt.
    num_s1 = int(num_populated_cells * s1_ratio)
    num_s2 = int(num_populated_cells * s2_ratio)
    num_s3 = int(num_populated_cells * s3_ratio)
    # Rest of the cells must be the remaining level of doubt, S4.

    # Mix again between the different level of doubts.
    np.random.shuffle(populated_cells_idx)

    # Calculate the number of indices so each part will be the size of the corresponding level of doubt.
    # First level of doubt will be index 0 until the number of cells for S1 are chosen.
    split_index_s1 = num_s1
    # Second level of doubt will start at the last index of S1, and will take over num_s2 cells, meaning it will finish
    # in cell split_index_s1 + num_s2.
    split_index_s2 = split_index_s1 + num_s2
    # Same as we explained above, index of S4 will just be the rest of the array.
    split_index_s3 = split_index_s2 + num_s3

    # Now we split the array into four parts corresponding to the indices calculated above.
    s1_indices = populated_cells_idx[:split_index_s1]
    s2_indices = populated_cells_idx[split_index_s1:split_index_s2]
    s3_indices = populated_cells_idx[split_index_s2:split_index_s3]
    s4_indices = populated_cells_idx[split_index_s3:]

    # Use unravel_index to map the indices from the 1D cell_indices array, to their corresponding row and column
    # positions in the 2D grid. This function takes the index from the 1D array (s1_indices, s2_indices, etc.)
    # and the size of the target 2D array (in our case, 100x100), then places the respective doubt level value
    # (1, 2, 3, or 4) into the corresponding position in the board.
    board[np.unravel_index(s1_indices, size)] = 1
    board[np.unravel_index(s2_indices, size)] = 2
    board[np.unravel_index(s3_indices, size)] = 3
    board[np.unravel_index(s4_indices, size)] = 4

    # Return the board after it was randomly initialized.
    return board, num_populated_cells


def get_neighbors(grid, row, col):
    """
    :param grid: 2D array
    :param row: Row index of the person spreading the rumor.
    :param col: Column index of the person spreading the rumor.
    :return: List of neighboring cells' indices.
    """
    # Unpack the Dimension of the grid.
    rows, cols = grid.shape

    # Calculate the indices of each potential neighbor.
    top_neighbor = (row + 1, col)
    top_right_neighbor = (row + 1, col+1)
    right_neighbor = (row, col + 1)
    bottom_right_neighbor = (row - 1, col + 1)
    bottom_neighbor = (row - 1, col)
    bottom_left_neighbor = (row - 1, col - 1)
    left_neighbor = (row, col - 1)
    top_left_neighbor = (row + 1, col - 1)
    # Create a list of potential neighbors' indices.
    potential_neighbors = [top_neighbor, top_right_neighbor, right_neighbor, bottom_right_neighbor, bottom_neighbor,
                           bottom_left_neighbor, left_neighbor, top_left_neighbor]

    # Create a list to store all the valid neighbors indices.
    valid_neighbors = []

    # Iterate through the potential neighbors.
    for r, c in potential_neighbors:
        if ((0 > r or r >= rows) or (0 > c or c >= cols)) or (grid[r, c] == -1):
            continue
        # Check if the neighbor's row and column indices are within the grid's boundaries.
        if 0 <= r < rows and 0 <= c < cols:
            # If the neighbor is within the grid, append its coordinates to the valid_neighbors list.
            valid_neighbors.append((r, c))

    # Return the list of valid_neighbors.
    return valid_neighbors


def get_probabilities():
    """
    :return: Dictionary in which the key is the doubt level and the value is the probability he will believe a rumor.
    """
    return {1: 1.0, 2: 2/3, 3: 1/3, 4: 0.0}


def spread_rumor(board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board):
    """
    :param board: (np.array) Matrix with each cell containing the person's level of doubt.
    :param L: The amount of generations a rumor spreader waits before spreading a rumor again if he encounters one.
    :param banned_rumor_spreaders: Dictionary that save in each cell the number of generations (L) a rumor spreader
           waits before spreading a rumor again. Each iteration we update this matrix as generations pass.
    :return: Update matrix grid and update matrix of rumor_spreaders.
    """

    # Create a copy of the board, so we can hold the updated doubt levels as results of spreading a rumor.
    new_board = np.copy(board)
    # Create a np array and initialize it with zeros as the size of the grid.
    # We will store in this array the number of rumors that each cell received in this iteration. So if needed we will
    # change the doubt level. (if a cell received at least two rumors in the same iteration).
    current_rumor_received = np.zeros(board.shape)
    # Store a dictionary of each doubt level to the corresponding probability.
    probabilities = get_probabilities()

    # Nested loop iterating on each cell in the grid.
    for row, col in np.argwhere(flags_board):

        # if the cell value is -1 this means the cell is unpopulated, white.
        if original_doubt_lvl_spreaders[row, col] == -1:
            flags_board[row, col] = False
            continue

        # Check if the current cell in the grid is not banned from spreading rumors.
        if (row, col) in banned_rumor_spreaders:
            # If the cell has less than the value L, it can't spread a rumor,
            # so instead we will increment the value of generations he waited.
            # Else, the cell has waited L generation, so now he can spread the rumor.
            if banned_rumor_spreaders[(row, col)] < L:
                banned_rumor_spreaders[(row, col)] += 1
                continue
            else:
                del banned_rumor_spreaders[(row, col)]
                new_board[row, col] = original_doubt_lvl_spreaders[row, col]

        # Checking in the rumor_received matrix if the cell received the rumour from two or more neighbors.
        # If so, the cell will temporarily reduce its level of doubt when deciding whether to spread the rumour.
        # Else, the level of doubt will stay the same as it was originally set.
        if rumor_received[row, col] >= 1:
            doubt_level = max(1, original_doubt_lvl_spreaders[row, col] - 1)
        else:
            doubt_level = original_doubt_lvl_spreaders[row, col]

        # Store the probability of the cell to spread the rumour he received.
        probability = probabilities[doubt_level]

        # Retrieve the neighbors of the current cell.
        neighbors = get_neighbors(original_doubt_lvl_spreaders, row, col)

        for r, c in neighbors:
            # Check if my neighbor spread a rumour, so we won't spread the rumor again to him (our rule we enforce here)
            # also check if the cell we are looking at is populated.
            if original_doubt_lvl_spreaders[r, c] == -1 or (r, c) in banned_rumor_spreaders:
                continue
            else:
                # We randomly choose a number between 0 and 1. if this number is lower than the
                # probability of the cell to believe a rumour, the cell will spread the rumour to the valid neighbor.
                if np.random.random() < probability:
                    # Change the neighbor cell to 'true' (active cell that is going to spread a rumour).
                    flags_board[r, c] = True
                    # Change the state of the cell that currently spread the rumor to his neighbor.
                    new_board[row, col] = 5
                    # Increment the counter of the neighbor to keep track how many people spread him the rumor.
                    # So in the next generation when it is his turn to spread the rumor he will know from how many
                    # cells we received the rumor, and who not to send to again.
                    current_rumor_received[r, c] += 1
                    # Add the current spreading rumor cell to the banned list of spreading rumor.
                    banned_rumor_spreaders[(row, col)] = 0
    # Retrieve number of cells that are populated.
    total_population = np.sum(new_board != -1)
    # Cells who receive the rumour, their state will be 'true'.
    exposed_population = np.sum(flags_board)
    # Calculate exposed_population in percentages.
    exposed_percentages = (exposed_population / total_population) * 100
    # Round the number to three points after the dot.
    rounded_percentage = round(exposed_percentages, 3)

    return new_board, banned_rumor_spreaders, current_rumor_received, flags_board, rounded_percentage


def initialize_board_Layers(size, P, s1_ratio, s2_ratio, s3_ratio):
    """
      :param size: This value sets the height and width of the grid.
      :param s1_ratio: The proportion of the top rectangle of people who will believe every rumor they hear.
      :param s2_ratio: The proportion of the second rectangle of people who will believe a rumor with a 2/3 probability.
      :param s3_ratio: The proportion of the third rectangle of people who will believe a rumor with a 1/3 probability.
      :return: Initialized board of each cell with its state of level of doubt.
    """
    rows, cols = size  # Unpack the dimensions of the grid.
    board = np.full(size, -1)  # Initialize an empty board with -1 in all cells.
    # Define the layer doubt of level height by the ratio of each doubt of level.
    layer_1_height = int(rows * s1_ratio)
    layer_2_height = int(rows * s2_ratio)
    layer_3_height = int(rows * s3_ratio)

    # Nested loop to iterate over all the board.
    for i in range(rows):
        for j in range(cols):
            # We randomly choose a number between 0 and 1. if this number is lower than P, the probability the cell
            # is populated, we will populate the cell!
            if np.random.random() < P:
                # Populate the first layer of doubt of level 1 until getting to the point that layer 2 needs to start.
                if i < layer_1_height:
                    board[i, j] = 1
                # Populate the cells with doubt of level 2 until the point that level 3 height starts.
                elif i < layer_1_height + layer_2_height:
                    board[i, j] = 2
                # Populated the cells with doubt of level 3 until the point that level 4 height starts.
                elif i < layer_1_height + layer_2_height + layer_3_height:
                    board[i, j] = 3
                # Rest of the board are doubt level 4.
                else:
                    board[i, j] = 4

    # Calculate the number of cells that are populated, needed to be all cells that their state are not equal to -1.
    num_populated_cells = 0
    for i in range(rows):
        for j in range(cols):
            if board[i, j] != -1:
                num_populated_cells += 1

    return board, num_populated_cells


def initialize_board_half_half(size, P, s1_ratio, s2_ratio, s3_ratio):
    """
    :param size: This value sets the height and width of the grid.
    :param P: The overall density of the population.
    :param s1_ratio: The proportion of people who will believe every rumor they hear.
    :param s2_ratio: The proportion of people who will believe a rumor with a 2/3 probability.
    :param s3_ratio: The proportion of people who will believe a rumor with a 1/3 probability.
    :return: Initialized board with each cell's level of doubt.
             Also return the number of cells that are populated.
    """
    rows, cols = size  # Unpack the dimensions of the grid.
    board = np.full(size, -1)  # Initialize an empty board with -1 in all cells.

    # Calculate s4_ratio ration.
    s4_ratio = 1 - (s1_ratio + s2_ratio + s3_ratio)

    for i in range(rows):
        for j in range(cols):
            # We randomly choose a number between 0 and 1. If this number is lower than P, the probability the cell
            # is populated, we will populate the cell!
            if np.random.random() < P:
                # Populate the main diagonal with a mixed level of doubt.
                # Each level of doubt can be selected depending on the ratio of the parameters.
                if i == j:
                    board[i, j] = np.random.choice([1, 2, 3, 4],
                                                   p=[s1_ratio, s2_ratio, s3_ratio, s4_ratio])
                # Populated the upper triangle with level of doubt s1 / s2 depending on their ratio.
                elif i < j:
                    board[i, j] = np.random.choice([1, 2],
                                                   p=[s1_ratio / (s1_ratio + s2_ratio), s2_ratio / (s1_ratio + s2_ratio)])
                # Populate the bottom triangle with level of doubt s3 / s4 depending on their ratio.
                else:
                    board[i, j] = np.random.choice([3, 4],
                                                   p=[s3_ratio / (s3_ratio + s4_ratio), s4_ratio / (s3_ratio + s4_ratio)])

    # Calculate the number of cells that are populated, needs to be all cells that their state is not equal to -1.
    num_populated_cells = 0
    for i in range(rows):
        for j in range(cols):
            if board[i, j] != -1:
                num_populated_cells += 1

    return board, num_populated_cells


def initialize_board_nested_rectangles(size, P):
    """
    :param size: This value sets the height and width of the grid.
    :param P: The overall density of the population.
    :return: Initialized board with each cell's level of doubt.
             Also return the number of cells that are populated.
    """
    rows, cols = size  # Unpack the dimensions of the grid.
    board = np.full(size, -1)  # Initialize an empty board with -1 in all cells.
    # Define the number size of reach rectangle:
    layer_1_thickness = 6
    layer_2_thickness = 9
    layer_3_thickness = 11
    layer_4_thickness = 50

    # Nested loop going over each cell in the board.
    for i in range(rows):
        for j in range(cols):
            # We randomly choose a number between 0 and 1. if this number is lower than P, the probability the cell
            # is populated, we will populate the cell!
            if np.random.random() < P:
                # Define the cells in the outer layer (RED).
                if i < layer_1_thickness or j < layer_1_thickness or i >= rows - layer_1_thickness or j >= cols - layer_1_thickness:
                    board[i, j] = 4
                # Define the cells in the layer doubt of level 3 (ORANGE).
                elif i < layer_1_thickness + layer_2_thickness or j < layer_1_thickness + layer_2_thickness or i >= rows - (
                        layer_1_thickness + layer_2_thickness) or j >= cols - (layer_1_thickness + layer_2_thickness):
                    board[i, j] = 3
                # Define the cells in the layer doubt of level 2 (GREEN).
                elif i < layer_1_thickness + layer_2_thickness + layer_3_thickness or j < layer_1_thickness + layer_2_thickness + layer_3_thickness or i >= rows - (
                        layer_1_thickness + layer_2_thickness + layer_3_thickness) or j >= cols - (
                        layer_1_thickness + layer_2_thickness + layer_3_thickness):
                    board[i, j] = 2
                # Define the cells in the inner layer (BLUE).
                elif i < layer_1_thickness + layer_2_thickness + layer_3_thickness + layer_4_thickness and j < layer_1_thickness + layer_2_thickness + layer_3_thickness + layer_4_thickness:
                    board[i, j] = 1

    # Calculate the number of cells that are populated, needs to be all cells that their state is not equal to -1.
    num_populated_cells = 0
    for i in range(rows):
        for j in range(cols):
            if board[i, j] != -1:
                num_populated_cells += 1

    return board, num_populated_cells
