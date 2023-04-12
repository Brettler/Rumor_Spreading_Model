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
    # Rest of the cells must be the remaining levels of doubt, S4.

    # Mix again between the different level of doubts.
    np.random.shuffle(populated_cells_idx)

    # Calculate the indexes we need to pick so that each part will be the size of the corresponding level of doubt.
    # First level of doubt will be index 0 until the number of cells for S1 are taken.
    split_index_s1 = num_s1
    # Second level of doubt will start at the index S1 ended and will take over num_s2 cells, meaning it will finish
    # in cell split_index_s1 + num_s2.
    split_index_s2 = split_index_s1 + num_s2
    # Same as we explained above, index of S4 will just be the rest of the array.
    split_index_s3 = split_index_s2 + num_s3

    # Now we split the array into four parts corresponding to the split indices we calculated.
    s1_indices = populated_cells_idx[:split_index_s1]
    s2_indices = populated_cells_idx[split_index_s1:split_index_s2]
    s3_indices = populated_cells_idx[split_index_s2:split_index_s3]
    s4_indices = populated_cells_idx[split_index_s3:]

    # Use unravel_index to map the indices from the 1D cell_indices array, to their corresponding row and column
    # positions in the 2D grid. The function takes the index from the 1D array (s1_indices, s2_indices, etc.)
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
    :param row: Index of the row of the person who spreading the rumor.
    :param col:Index of the column of the person who spreading the rumor.
    :return: List of neighboring cells' indices.
    """
    # Unpack the Dimensional of the grid.
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
    # Creat a list of potential neighbors indices.
    potential_neighbors = [top_neighbor, top_right_neighbor, right_neighbor, bottom_right_neighbor, bottom_neighbor,
                           bottom_left_neighbor, left_neighbor, top_left_neighbor]
    #potential_neighbors = [top_neighbor, right_neighbor, bottom_neighbor, left_neighbor]
    # Create a list to store all the valid neighbors indices.
    valid_neighbors = []

    # Iterate through the potential neighbors
    for r, c in potential_neighbors:
        if ((0 > r or r >= rows) or (0 > c or c >= cols)) or (grid[r, c] == -1):
            continue
        # Check if the neighbor's row and column indices are within the grid's boundaries
        if 0 <= r < rows and 0 <= c < cols:
            # If the neighbor is within the grid, append its coordinates to the valid_neighbors list
            valid_neighbors.append((r, c))

    # Return the list of valid_neighbors
    return valid_neighbors


def get_probabilities():
    """
    :return: Dictionary which key is the doubt level and the value is the probability he will believe a rumor.
    """
    return {1: 1.0, 2: 2/3, 3: 1/3, 4: 0.0}


def spread_rumor(board, banned_rumor_spreaders, L, original_doubt_lvl_spreaders, rumor_received, flags_board):
    """
    :param board: (np.array) Matrix with each cell containing the person's level of doubt.
    :param L: The amount of generations a rumor spreader waits before spreading a rumor again if he encounters one.
    :param banned_rumor_spreaders: Dictionary that save in each cell he number (L) of generations a rumor spreader waits
                            before spreading a rumor again. each iteration we update this matrix as generation pass's.
    :return: Update matrix grid and update matrix of rumor_spreaders.
    """

    # Create a copy of the board, so we can hold the updated doubt levels as results of spreading a rumor.
    new_board = np.copy(board)
    # Create np array and initialized it with zeros in the size of the grid.
    # We will store in this array the number of rumors that each cell received in this iteration. So if needed we will
    # change the doubt level. (if a cell received at least 2 rumors at the same iteration).
    current_rumor_received = np.zeros(board.shape)
    # Store the dictionary of each doubt level to the corresponding probability.
    probabilities = get_probabilities()

    # Nested loop iterating on each cell in the grid.
    for row, col in np.argwhere(flags_board):

        # if the cell value is -1 this means the cell is unpopulated
        if original_doubt_lvl_spreaders[row, col] == -1:
            flags_board[row, col] = False
            continue

        # Check if the correct cell in the grid is not banned from spreading rumors.
        if (row, col) in banned_rumor_spreaders:
            # If the cell still have less than value L it cant spread a
            # rumor so we will increament the value of generations he waited.
            # Else The cell have been waited for L generation so this generation he can spread the rumor.
            if banned_rumor_spreaders[(row, col)] < L:
                banned_rumor_spreaders[(row, col)] += 1
                continue
            else:
                del banned_rumor_spreaders[(row, col)]
                new_board[row, col] = original_doubt_lvl_spreaders[row, col]

        # Checking in rumor_received matrix if the cell received the rumor from 2 or above neighbors.
        # If the cell received the rumor he currently wants to spread from more than two neighbors
        # If the above true, the cell will temporarily reduce his level of doubt when
        # he decides if to spread to rumor or not.
        # Else, the level of doubt stay the same as it was originally set.
        if rumor_received[row, col] >= 1:
            doubt_level = max(1, original_doubt_lvl_spreaders[row, col] - 1)
        else:
            doubt_level = original_doubt_lvl_spreaders[row, col]

        # Store the probability of the cell to spread the rumor he received.
        probability = probabilities[doubt_level]

        neighbors = get_neighbors(original_doubt_lvl_spreaders, row, col)

        counter_rumors_expose = 0
        for r, c in neighbors:
            if original_doubt_lvl_spreaders[r, c] == -1 or (r, c) in banned_rumor_spreaders:
                continue
            else:

                if np.random.random() < probability:
                    counter_rumors_expose += 1
                    flags_board[r, c] = True
                    new_board[row, col] = 5
                    current_rumor_received[r, c] += 1

                    banned_rumor_spreaders[(row, col)] = 0

    total_population = np.sum(new_board != -1)
    exposed_population = np.sum(flags_board)
    exposed_percentages = (exposed_population / total_population) * 100

    return new_board, banned_rumor_spreaders, current_rumor_received, flags_board, exposed_percentages


def initialize_board_Layers(size, P, s1_ratio, s2_ratio, s3_ratio):
    """
      :param size: This value sets the height and width of the grid
      :param s1_ratio: The proportion of the innermost rectangle for people who will believe every rumor they hear
      :param s2_ratio: The proportion of the second rectangle for people who will believe a rumor with a 2/3 probability
      :param s3_ratio: The proportion of the third rectangle for people who will believe a rumor with a 1/3 probability
      :return: Initialized board will each cell with state of level of doubt.
    """
    rows, cols = size
    board = np.full(size, -1)

    layer_1_height = int(rows * s1_ratio)
    layer_2_height = int(rows * s2_ratio)
    layer_3_height = int(rows * s3_ratio)
    layer_4_height = rows - (layer_1_height + layer_2_height + layer_3_height)

    for i in range(rows):
        for j in range(cols):
            if np.random.random() < P:
                if i < layer_1_height:
                    board[i, j] = 1
                elif i < layer_1_height + layer_2_height:
                    board[i, j] = 2
                elif i < layer_1_height + layer_2_height + layer_3_height:
                    board[i, j] = 3
                else:
                    board[i, j] = 4

    return board


def initialize_board_half_half(size, s1_ratio, s2_ratio, s3_ratio):
    rows, cols = size
    board = np.full(size, -1)
    # Calculate s4_ratio ration.
    s4_ratio = 1 - (s1_ratio + s2_ratio + s3_ratio)

    for i in range(rows):
        for j in range(cols):
            if i == j:
                board[i, j] = np.random.choice([1, 2, 3, 4],
                                               p=[s1_ratio, s2_ratio, s3_ratio, 1 - (s1_ratio + s2_ratio + s3_ratio)])
            elif i < j:
                board[i, j] = np.random.choice([1, 2],
                                               p=[s1_ratio / (s1_ratio + s2_ratio), s2_ratio / (s1_ratio + s2_ratio)])
            else:
                board[i, j] = np.random.choice([3, 4],
                                               p=[s3_ratio / (s3_ratio + s4_ratio), s4_ratio / (s3_ratio + s4_ratio)])

    return board


def initialize_board_nested_rectangles(size):

    rows, cols = size
    board = np.full(size, -1)

    layer_1_thickness = 20
    layer_2_thickness = 15
    layer_3_thickness = 10
    layer_4_thickness = 10

    for i in range(rows):
        for j in range(cols):
            if i < layer_1_thickness or j < layer_1_thickness or i >= rows - layer_1_thickness or j >= cols - layer_1_thickness:
                board[i, j] = 4
            elif i < layer_1_thickness + layer_2_thickness or j < layer_1_thickness + layer_2_thickness or i >= rows - (
                    layer_1_thickness + layer_2_thickness) or j >= cols - (layer_1_thickness + layer_2_thickness):
                board[i, j] = 3
            elif i < layer_1_thickness + layer_2_thickness + layer_3_thickness or j < layer_1_thickness + layer_2_thickness + layer_3_thickness or i >= rows - (
                    layer_1_thickness + layer_2_thickness + layer_3_thickness) or j >= cols - (
                    layer_1_thickness + layer_2_thickness + layer_3_thickness):
                board[i, j] = 2
            elif i < layer_1_thickness + layer_2_thickness + layer_3_thickness + layer_4_thickness and j < layer_1_thickness + layer_2_thickness + layer_3_thickness + layer_4_thickness:
                board[i, j] = 1

    return board
