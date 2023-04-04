import numpy as np
import random


def initialize_board(size, s1_ratio, s2_ratio, s3_ratio):
    # Unpack the Dimensional of the grid.
    rows, cols = size
    # Init empty board with 0 in all cells.
    board = np.zeros(size, dtype=np.uint8)
    # Calculate number of cells.
    total_cells = rows * cols
    # Calculate the number of cells for each level of doubt.
    num_s1 = int(total_cells * s1_ratio)
    num_s2 = int(total_cells * s2_ratio)
    num_s3 = int(total_cells * s3_ratio)
    # Rest of the cells must be the leftover level of doubt.
    num_s4 = total_cells - num_s1 - num_s2 - num_s3

    # Creat np array in the size of cells in the game.
    # Fill this array with the indexes of the cells and then shuffle it.
    cells_idx = np.random.permutation(total_cells)

    # Calculate the indexes we need to pick such that each part will be the size of the coressponding level of doubt.
    # First level of doubt will be index 0 until number of cells s1 is taking.
    split_index_s1 = num_s1
    # Second level of doubt will start in the index s1 finished and will take over num_s2 cells, meaning it will finish
    # in cell split_index_s1 + num_s2.
    split_index_s2 = split_index_s1 + num_s2
    # Same as we explain above. index of s4 will just be the rest of the array.
    split_index_s3 = split_index_s2 + num_s3

    # Now we split the np array into four parts corresponding to the splits index we calculate.
    s1_indices = cells_idx[:split_index_s1]
    s2_indices = cells_idx[split_index_s1:split_index_s2]
    s3_indices = cells_idx[split_index_s2:split_index_s3]
    s4_indices = cells_idx[split_index_s3:]

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


def spread_rumor(board, L, banned_rumor_spreaders):
    """
    :param board: Matrix such that in each cell we store the person level of doubt.
    :param L: The amount of generations a rumor spreader waits before spreading a rumor again if he encounters one.
    :param banned_rumor_spreaders: Matrix that save in each cell he number (L) of generations a rumor spreader waits
                            before spreading a rumor again. each iteration we update this matrix as generation pass's.
    :return: Update matrix grid and update matrix of rumor_spreaders.
    """
    # Unpack the Dimensional of the grid.
    rows, cols = board.shape
    # Create a copy of the board, so we can hold the updated doubt levels as results of spreading a rumor.
    new_board = np.copy(board)
    # Create np array and initialized it with zeros in the size of the grid.
    # We will store in this array the number of rumors that each cell received in this iteration. So if needed we will
    # change the doubt level. (if a cell received at least 2 rumors at the same iteration).
    rumor_received = np.zeros(board.shape)
    # Store the dictionary of each doubt level to the corresponding probability.
    probabilities = get_probabilities()

    # Nested loop iterating on each cell in the grid.
    for row in range(rows):
        for col in range(cols):
            # Check if the correct cell in the grid is not banned from spreading rumors.
            if banned_rumor_spreaders[row, col] == 0:
                # If the cell can spread a rumor we will get the neighbors of this cell, so we know which cells need to
                # receive the rumor.
                neighbors = get_neighbors(board, row, col)

                # Iterates on each neighbor in the list.
                for r, c in neighbors:
                    # Implementation of the rule:
                    # Generating random number between 0 and 1. If it is less than the probability corresponding to
                    # the level of doubt of the neighbor, the neighbor will accept the rumor.
                    if random.random() < probabilities[board[r, c]]:
                        # Update the matrix that counts the number of rumors each neighbor
                        # receive in the current iteration
                        rumor_received[r, c] += 1
    """
    banned_rumor_spreaders[banned_rumor_spreaders > 0] -= 1
    new_rumor_spreaders = (rumor_received >= 2) & (banned_rumor_spreaders == 0)
    banned_rumor_spreaders[new_rumor_spreaders] = L

    return new_board, banned_rumor_spreaders
    """
    # Update the doubt level of the neighbors temporarily if they received the rumor from at least two other neighbors.
    temporarily_reduced_doubt_level = (rumor_received >= 2)
    new_board[temporarily_reduced_doubt_level] = np.maximum(1, new_board[temporarily_reduced_doubt_level] - 1)

    # Decrease the countdown timers for all cells that are currently banned from spreading rumors.
    banned_rumor_spreaders[banned_rumor_spreaders > 0] -= 1

    # Update the banned_rumor_spreaders array based on cells that have received the rumor from at least 2 neighbors.
    new_rumor_spreaders = (rumor_received >= 2) & (banned_rumor_spreaders == 0)
    banned_rumor_spreaders[new_rumor_spreaders] = L

    return new_board, banned_rumor_spreaders




def run_spreading_rumors(iterations, size=(100, 100), s1_ratio=0.25, s2_ratio=0.25, s3_ratio=0.25, L=5):
    board = initialize_board(size, s1_ratio, s2_ratio, s3_ratio)
    rumor_spreaders = np.zeros(size, dtype=np.uint8)

    # Randomly select a person to start spreading the rumor
    start_row, start_col = np.random.randint(0, size[0]), np.random.randint(0, size[1])
    rumor_spreaders[start_row, start_col] = L

    for i in range(iterations):
        print(f"Iteration {i}:")
        print(board)
        board, rumor_spreaders = spread_rumor(board, L, rumor_spreaders)

    return board
