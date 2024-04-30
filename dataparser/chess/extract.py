import wget
import os
import patoolib
import chess.pgn
import io
import json
from tqdm import tqdm
from multiprocess import Pool
import random 

include_moves = False
process_num_games = 10_000

# Download the dataset
url = "https://archive.org/download/KingBase2019/KingBase2019-pgn.zip"
zip_file = "KingBase2019-pgn.zip"
extract_dir = "KingBase2019-pgn"

if not os.path.exists(extract_dir) and not os.path.exists(zip_file):
    print("Downloading the dataset...")
    zip_path = wget.download(url)
    print("Download complete.")

    print("Extracting the zip file...")
    patoolib.extract_archive(zip_path, outdir=extract_dir)
    print("Extraction complete.")

    # Clean up the downloaded zip file
    os.remove(zip_path)
else:
    print("The dataset is already downloaded and extracted.")

# Extract the games from all the PGN files in the directory
pgn_files = [file for file in os.listdir(extract_dir) if file.endswith(".pgn")]
total_files = len(pgn_files)
games_to_process_per_file = [ process_num_games // total_files ] * total_files
if sum(games_to_process_per_file) < process_num_games:
    games_to_process_per_file[-1] += process_num_games - sum(games_to_process_per_file)
games_to_process_per_file_mapping = { }
for i, file in enumerate(pgn_files):
    games_to_process_per_file_mapping[file] = games_to_process_per_file[i]

def get_winner(game):
    result = game.headers["Result"]
    
    if result == "1-0":
        return "white"
    elif result == "0-1":
        return "black"
    else:
        return None

def process_file(file_name):
    pgn_file = os.path.join(extract_dir, file_name)
    num_games_to_process = games_to_process_per_file_mapping[file_name]
    lines = set(random.choices(list(range(num_games_to_process)), k=num_games_to_process))
    # print(lines)
    with open(pgn_file, encoding='latin-1') as pgn:
        if not os.path.exists('data'):
            os.makedirs('data')
        with io.open(f'data/{file_name}.json', 'w', encoding='utf-8') as json_file:
            line_i = 0
            while game := chess.pgn.read_game(pgn):
                if line_i not in lines: 
                    line_i += 1
                    # print(f"index {line_i} is not in lines, moving on")
                    continue
                line_i += 1
                winner = get_winner(game)
                def role_of_index(i):
                    if winner == "white":
                        if i % 2 == 1: return "assistant"
                        else: return "user"
                    elif winner == "black":
                        if i % 2 == 0: return "user"
                        else: return "assistant"
                if winner != None:
                    try:
                        board_states = []
                        legal_moves = []
                        moves = []
                        board = chess.Board()
                        for num, move in enumerate(game.mainline_moves()):
                            moves.append(f"{num // 2 + 1}{'.' * (1 if num % 2 == 0 else 3)}{board.san(move)}")
                            board.push(move)
                            board_states.append(board.fen())
                            legal_moves.append([board.san(move) for move in board.legal_moves])
                        json_file.write(json.dumps({"messages" : [{"role" : "system", "content" : f"{winner} won the following chess game"}] + \
                                                    [
                                                    { 
                                                        "role" : role_of_index(i), 
                                                        "content" : move,
                                                        "fen" : board_states[i],
                                                        "legal_moves": legal_moves[i]
                                                    } if include_moves else { 
                                                        "role" : role_of_index(i), 
                                                        "content" : move,
                                                        "fen" : board_states[i],
                                                    }
                                                      for i, move in enumerate(moves)]}, ensure_ascii=False))
                        json_file.write('\n')
                    except Exception as e:
                        print(f"Error processing game in {pgn_file}: {e}")
                        continue

    
with tqdm(total=total_files, unit="file") as pbar:  
    with Pool(processes=8) as pool:
        for _ in pool.imap_unordered(process_file, pgn_files):
            pbar.update(1)