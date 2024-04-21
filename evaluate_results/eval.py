import chess
import ast
import json

RESULTS = "results/results_temp.json"

results = []
with open(RESULTS, mode='r') as f:
    nested_list = ast.literal_eval(f.read())
    for moves in nested_list:
        results.append(moves)

num_moves = len(results)
num_games = len(results[0])
results = [[ results[j][i] for j in range(num_moves)] for i in range(num_games)]

def cleanup(game): 
    def cleanup_move(move):
        move = move.split("</s>")[0]
        move = move.split("\n\n")[0]
        move = move.replace("...", ".")
        move = move.strip()
        return move
    return [ cleanup_move(move) for move in game ]

results = [ cleanup(game) for game in results ]

DATA_SIZE = len(results)
print(f"loaded {DATA_SIZE} games from {RESULTS}")
DATA = "prompts/prompts_test_sft.json"

data = []
with open(DATA, mode='r') as f:
    num_lines = 0
    for line in f: 
        if num_lines >= DATA_SIZE:
            break
        num_lines += 1
        data.append(line)

GAME_STARTS_FROM_IDX = 2
actual_moves = []
for game in data:
    game_json = json.loads(game)
    messages = game_json["messages"][GAME_STARTS_FROM_IDX:]
    moves = []
    for move in messages:
        moves.append(move["content"])
    actual_moves.append(moves)

boards = [ chess.Board() for _ in range(DATA_SIZE) ]

valid_moves = 0
total_moves = 0
for i in range(num_moves * 2):
    for j in range(DATA_SIZE):
        if i >= len(actual_moves[j]): continue
        if i % 2 == 0:
            try: 
                board = boards[j].copy()
                board.push_san(results[j][i].split(".")[1])
                valid_moves += 1
            except Exception as e: pass
            total_moves += 1
        boards[j].push_san(actual_moves[j][i].split(".")[1])
print(f"moves in each game f{[len(actual_moves[i]) for i in range(DATA_SIZE)]}")
print(f"number of moves in {RESULTS} is {num_moves * 2} in each game")
print(f"total moves: {total_moves}")
print(f"valid moves: {valid_moves}")
print(f"valid move accuracy: {valid_moves / (num_moves * DATA_SIZE) * 100:.2f}%")