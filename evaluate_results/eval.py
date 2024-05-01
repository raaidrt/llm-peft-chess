import chess
import ast
import json

import argparse

def evaluate_result(results_file, test_file):
    results = []
    START_ACTUAL_MOVES_FROM = 1
    with open(results_file, mode="r") as f:
        nested_list = ast.literal_eval(f.read())
        nested_list = nested_list[START_ACTUAL_MOVES_FROM:]
        for moves in nested_list:
            results.append(moves)

    num_moves = len(results)
    num_games = len(results[0])
    results = [[results[j][i] for j in range(num_moves)] for i in range(num_games)]

    def cleanup_move(move):
        move = move.split("</s>")[0]
        move = move.split("\n\n")[0]
        move = move.replace("...", ".")
        move = move.strip()
        return move

    def cleanup(game):
        return [cleanup_move(move) for move in game]


    results = [cleanup(game) for game in results]

    DATA_SIZE = len(results)
    print(f"loaded {DATA_SIZE} games from {results_file}")

    data = []
    with open(test_file, mode="r") as f:
        num_lines = 0
        for line in f:
            if num_lines >= DATA_SIZE:
                break
            num_lines += 1
            data.append(line)

    GAME_STARTS_FROM_IDX = 1
    actual_moves = []
    for game in data:
        game_json = json.loads(game)
        messages = game_json["messages"][GAME_STARTS_FROM_IDX:]
        moves = []
        for move in messages:
            moves.append(move["content"])
        actual_moves.append(moves)

    boards = [chess.Board() for _ in range(DATA_SIZE)]

    def cleanup_move_for_evaluation(move):
        move = cleanup_move(move) 
        move = move.split(".")[1]
        move = move.split()[0]
        return move

    valid_moves = 0
    total_moves = 0
    ACTUAL_MOVES_START_FROM = 0
    for i in range(num_moves * 2):
        for j in range(DATA_SIZE):
            if i >= len(actual_moves[j]):
                continue
            if i >= ACTUAL_MOVES_START_FROM:
                try:
                    # print(f"actual move: {cleanup_move(actual_moves[j][i]).split('.')[1].split()[0]}, predicted move: {cleanup_move(results[j][i - ACTUAL_MOVES_START_FROM]).split('.')[1].split()[0]}")
                    board = boards[j].copy()
                    board.push_san(cleanup_move_for_evaluation(results[j][i - ACTUAL_MOVES_START_FROM]))
                    board.pop()
                    valid_moves += 1
                except Exception as e:
                    pass
            total_moves += 1
            boards[j].push_san(cleanup_move_for_evaluation(actual_moves[j][i]))
    # print(f"moves in each game f{[len(actual_moves[i]) for i in range(DATA_SIZE)]}")
    print(f"number of moves in {results_file} is {num_moves * 2} in each game")
    print(f"total moves: {total_moves}")
    print(f"valid moves: {valid_moves}")
    print(f"valid move accuracy: {valid_moves / (num_moves * DATA_SIZE) * 100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=str)
    parser.add_argument("--testfile", type=str)
    args = parser.parse_args()
    results = args.results
    testfile = args.testfile
    evaluate_result(results, testfile)