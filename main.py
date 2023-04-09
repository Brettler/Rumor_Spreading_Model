import numpy as np



def initialize_board(size, P, s1_ratio, s2_ratio, s3_ratio):
    """
    :param size: This value sets the height and width of the grid
    :param P: The overall density of the population
    :param s1_ratio: The proportion of people who will believe every rumor they hear
    :param s2_ratio: The proportion of people who will believe a rumor with a 2/3 probability
    :param s3_ratio: The proportion of people who will believe a rumor with a 1/3 probability
    :return: Initialized board will each cell with state of level of doubt.
    """
    # Unpack the Dimensional of the grid.
    rows, cols = size
    # Init empty board with -1 in all cells.
    board = np.full(size, -1)
    # Calculate number of cells.
    total_cells = rows * cols
    # Calculate the number of populated cells based on population density P.
    num_populated_cells = int(total_cells * P)

    # Creat np array in the size of cells who are populated in the game.
    # Fill this array with the indexes corresponding the cells and then shuffle it.
    populated_cells_idx = np.random.permutation(total_cells)[:num_populated_cells]

    # Calculate the number of cells for each level of doubt.
    num_s1 = int(num_populated_cells * s1_ratio)
    num_s2 = int(num_populated_cells * s2_ratio)
    num_s3 = int(num_populated_cells * s3_ratio)
    # Rest of the cells must be the remaining levels of doubt.

    # Mix again between the different level of doubts.
    np.random.shuffle(populated_cells_idx)

    # Calculate the indexes we need to pick such that each part will be the size of the coressponding level of doubt.
    # First level of doubt will be index 0 until number of cells s1 is taking.
    split_index_s1 = num_s1
    # Second level of doubt will start in the index s1 finished and will take over num_s2 cells, meaning it will finish
    # in cell split_index_s1 + num_s2.
    split_index_s2 = split_index_s1 + num_s2
    # Same as we explain above. index of s4 will just be the rest of the array.
    split_index_s3 = split_index_s2 + num_s3

    # Now we split the np array into four parts corresponding to the splits index we calculate.
    s1_indices = populated_cells_idx[:split_index_s1]
    s2_indices = populated_cells_idx[split_index_s1:split_index_s2]
    s3_indices = populated_cells_idx[split_index_s2:split_index_s3]
    s4_indices = populated_cells_idx[split_index_s3:]

    # Use unravel_index to map the indices from the 1D cell_indices
    # array to their corresponding row and column positions in the 2D grid.
    # The function takes the index from the 1D array (s1_indices, s2_indices, etc.)
    # and the size of the target 2D array (in our case, 100x100),
    # and places the respective doubt level value (1, 2, 3, or 4) into the corresponding position in the board.
    board[np.unravel_index(s1_indices, size)] = 1
    board[np.unravel_index(s2_indices, size)] = 2
    board[np.unravel_index(s3_indices, size)] = 3
    board[np.unravel_index(s4_indices, size)] = 4

    # Return the board after it was randomly initialized.
    return board


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

    # Create a list to store all the valid neighbors indices.
    valid_neighbors = []

    # Iterate through the potential neighbors
    for r, c in potential_neighbors:
        if ((0 > r or r >= rows) or (0 > c or c >= cols)) or (grid[r, c] == -1):
            continue
        # Check if the neighbor's row and column indices are within the grid's boundaries
        # /// check if  the neighbor is -1 /////////////////////////////
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
    :param board: Matrix such that in each cell we store the person level of doubt.
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



def initialize_board_clusters(size, P, s1_ratio, s2_ratio, s3_ratio, cluster_size=10):
    # Initialize an empty board
    board = np.zeros(size, dtype=int)

    # Calculate the number of populated cells based on population density P
    total_cells = size[0] * size[1]
    n_populated = int(total_cells * P)

    # Calculate the number of clusters for each doubt level, scaled by the population density
    n_s1 = int(n_populated * s1_ratio)
    n_s2 = int(n_populated * s2_ratio)
    n_s3 = int(n_populated * s3_ratio)

    def grow_cluster(seed_x, seed_y, cluster_size, value):
        cluster_points = [(seed_x, seed_y)]
        board[seed_x, seed_y] = value
        for _ in range(cluster_size):
            if not cluster_points:
                break
            x, y = cluster_points.pop()
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for nx, ny in neighbors:
                if 0 <= nx < size[0] and 0 <= ny < size[1] and board[nx, ny] == 0:
                    board[nx, ny] = value
                    cluster_points.append((nx, ny))

    # Create clusters for each doubt level
    for _ in range(n_s1):
        seed_x, seed_y = np.random.randint(0, size[0]), np.random.randint(0, size[1])
        grow_cluster(seed_x, seed_y, cluster_size, 1)

    for _ in range(n_s2):
        seed_x, seed_y = np.random.randint(0, size[0]), np.random.randint(0, size[1])
        grow_cluster(seed_x, seed_y, cluster_size, 2)

    for _ in range(n_s3):
        seed_x, seed_y = np.random.randint(0, size[0]), np.random.randint(0, size[1])
        grow_cluster(seed_x, seed_y, cluster_size, 3)

    # Fill the remaining cells with immune individuals
    board[board == 0] = 0

    return board

