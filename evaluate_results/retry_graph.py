import ast

import matplotlib.pyplot as plt

with open("white_cp_dev.json", mode = "r") as f:
    white_cp_dev = ast.literal_eval(f.read())
with open("black_cp_dev.json", mode = "r") as f:
    black_cp_dev = ast.literal_eval(f.read())
with open("white_num_moves.json", mode = "r") as f:
    white_num_moves = ast.literal_eval(f.read())
with open("black_num_moves.json", mode = "r") as f:
    black_num_moves = ast.literal_eval(f.read())
TRUNCATE_WHITE = 120
white_move_numbers = [i + 1 for i in range(len(white_cp_dev))][:TRUNCATE_WHITE]
black_move_numbers = [i + 1 for i in range(len(black_cp_dev))][:TRUNCATE_WHITE]
white_weights = [white_num_moves[i] / white_num_moves[0] for i in range(len(white_cp_dev))][:TRUNCATE_WHITE]
black_weights = [black_num_moves[i] / black_num_moves[0] for i in range(len(black_cp_dev))][:TRUNCATE_WHITE]
white_cp_dev = [-abs(score) for score in white_cp_dev][:TRUNCATE_WHITE]
black_cp_dev = [-abs(score) for score in black_cp_dev][:TRUNCATE_WHITE]
with plt.style.context('bmh'):
    plt.figure(figsize=(10, 6))  # Set the figure size (width, height) in inches
    plt.scatter(white_move_numbers[0::2], white_cp_dev[0::2], color='blue', marker='o', alpha=white_weights[0::2], label="White Pieces")  # Create a scatterplot
    plt.scatter(white_move_numbers[1::2], white_cp_dev[1::2], color='red', marker='o', alpha=white_weights[1::2], label="Black Pieces")  # Create a scatterplot

    plt.xlabel('Move Number')  # Set the label for the x-axis
    plt.ylabel('Average Centipawn Deviation from Stockfish Optimum')  # Set the label for the y-axis
    plt.title('Average Move-wise Centipawn Deviation from Stockfish Optimum playing as White')  # Set the title of the plot

    plt.grid(True, alpha=0.5)
    # Set the x-axis ticks to show every 10th move number
    xticks = range(0, max(white_move_numbers)+1, 10)
    plt.xticks(xticks)
    plt.xlim([0, max(white_move_numbers)])
    plt.ylim([-500, 500])

    plt.legend(loc='lower right')

    # Save the graph to a specific file
    plt.savefig(f'graphs/white.png', dpi=300)

with plt.style.context('bmh'):
    plt.figure(figsize=(10, 6))  # Set the figure size (width, height) in inches
    plt.scatter(black_move_numbers[0::2], black_cp_dev[0::2], color='blue', marker='o', alpha=black_weights[0::2], label="White Pieces")  # Create a scatterplot
    plt.scatter(black_move_numbers[1::2], black_cp_dev[1::2], color='red', marker='o', alpha=black_weights[1::2], label="Black Pieces")  # Create a scatterplot

    plt.xlabel('Move Number')  # Set the label for the x-axis
    plt.ylabel('Average Centipawn Deviation from Stockfish Optimum')  # Set the label for the y-axis
    plt.title('Average Move-wise Centipawn Deviation from Stockfish Optimum playing as Black')  # Set the title of the plot

    plt.grid(True, alpha=0.5)
    # Set the x-axis ticks to show every 10th move number
    xticks = range(0, max(black_move_numbers)+1, 10)
    plt.xticks(xticks)
    plt.xlim([0, max(black_move_numbers)])
    plt.ylim([-500, 500])

    plt.legend(loc='lower right')

    # Save the graph to a specific file
    plt.savefig(f'graphs/black.png', dpi=300)