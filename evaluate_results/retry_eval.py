import asyncio
import chess
import chess.engine
import time
import ast
import multiprocess
import json
from tqdm.contrib import tenumerate

RESULTS = "retry_results/results_qlora_simple_retry.json"
PROMPTS = "prompts/prompts_test_sft.json"
white_max_moves = None
black_max_moves = None
white_games = []
white_actual_games = []
black_games = []
black_actual_games = []
actual_games = []
with open(RESULTS, mode="r") as f:
    nested_list = ast.literal_eval(f.read())
    for game in nested_list:
        if game[0].split()[0] == "black":
            black_games.append(game[1:])
            num_moves = len(black_games[-1])
            if black_max_moves is None or num_moves > black_max_moves:
                black_max_moves = num_moves
        else:
            white_games.append(game[1:])
            num_moves = len(white_games[-1])
            if white_max_moves is None or num_moves > white_max_moves:
                white_max_moves = num_moves
print(f"Processed {len(white_games)} white games and {len(black_games)} black games")
DATA_SIZE = len(white_games) + len(black_games)
with open(PROMPTS, mode="r") as f:
    all_games = f.readlines()[:DATA_SIZE]
    for line in all_games:
        game_json = json.loads(line)
        if game_json["messages"][0]["content"].split()[0] == "white":
            white_actual_games.append(game_json["messages"][1:])
        elif game_json["messages"][0]["content"].split()[0] == "black":
            black_actual_games.append(game_json["messages"][1:])

white_cp_deviations = [0.0 for _ in range(white_max_moves)]
black_cp_deviations = [0.0 for _ in range(black_max_moves)]
num_white_games_with_moves = [0 for _ in range(white_max_moves)]
num_black_games_with_moves = [0 for _ in range(black_max_moves)]

def process_move(move):
    move = move.replace("...", ".")
    return move.split(".")[1]


async def main() -> None:
    before = time.time()
    _, engine = await chess.engine.popen_uci(r"/Users/raaid/Downloads/stockfish/stockfish-macos-m1-apple-silicon")
    after = time.time()
    print(f"Engine started in {after - before} seconds")

    async def process_white_game(game_id, game):
        board = chess.Board()
        for i, actual_move in enumerate(game):
            if white_games[game_id][i] == "invalid":
                break
            move = process_move(white_games[game_id][i])
            result = await engine.play(board, chess.engine.Limit(time=0.1))
            engine_board = board.copy() 
            engine_board.push(result.move)
            engine_score = await engine.analyse(engine_board, chess.engine.Limit(time=0.1))
            engine_score = engine_score["score"].white().score(mate_score=100000)
            try: board.push_san(move)
            except Exception as e: continue
            num_white_games_with_moves[i] += 1
            our_score = await engine.analyse(board, chess.engine.Limit(time=0.1))
            our_score = our_score["score"].white().score(mate_score=100000)
            white_cp_deviations[i] += our_score - engine_score
            board.pop()
            board.push_san(process_move(actual_move["content"]))

    async def process_black_game(game_id, game):
        board = chess.Board()
        for i, actual_move in enumerate(game):
            if black_games[game_id][i] == "invalid":
                break
            move = process_move(black_games[game_id][i])
            result = await engine.play(board, chess.engine.Limit(time=0.1))
            engine_board = board.copy() 
            engine_board.push(result.move)
            engine_score = await engine.analyse(engine_board, chess.engine.Limit(time=0.1))
            engine_score = engine_score["score"].black().score(mate_score=100000)
            try: board.push_san(move)
            except Exception as e: continue
            num_black_games_with_moves[i] += 1
            our_score = await engine.analyse(board, chess.engine.Limit(time=0.1))
            our_score = our_score["score"].black().score(mate_score=100000)
            black_cp_deviations[i] += our_score - engine_score
            board.pop()
            board.push_san(process_move(actual_move["content"]))

    print("Processing the white games")
    for i, game in tenumerate(white_actual_games, start=1):
        await process_white_game(i - 1, game)
    print("Processing the black games")
    for i, game in enumerate(black_actual_games, start=1):
        await process_black_game(i - 1, game)

    def process_if_non_negative(dividend, divisor):
        if divisor > 0:
            return dividend / divisor
        else:
            return 0.0

    avg_deviations_white = [process_if_non_negative(white_cp_deviations[i], num_white_games_with_moves[i]) for i in range(white_max_moves)]
    avg_deviations_black = [process_if_non_negative(black_cp_deviations[i], num_black_games_with_moves[i]) for i in range(black_max_moves)]

    with open("white_cp_dev.json", mode="w") as f:
        f.write(str(avg_deviations_white))
    with open("black_cp_dev.json", mode="w") as f:
        f.write(str(avg_deviations_black))
    with open("white_num_moves.json", mode="w") as f:
        f.write(str(num_white_games_with_moves))
    with open("black_num_moves.json", mode="w") as f:
        f.write(str(num_black_games_with_moves))

    await engine.quit()

if __name__ == "__main__":
    asyncio.run(main())