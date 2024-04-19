import wget
import os
import patoolib
import chess.pgn
import io
import json
from tqdm import tqdm
from multiprocess import Pool

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
    with open(pgn_file, encoding='latin-1') as pgn:
        if not os.path.exists('data'):
            os.makedirs('data')
        with io.open(f'data/{file_name}.json', 'w', encoding='utf-8') as json_file:
            while game := chess.pgn.read_game(pgn):
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
                        moves = []
                        board = chess.Board()
                        for num, move in enumerate(game.mainline_moves(), start=1):
                            moves.append(f"{num}.{board.san(move)}")
                            board.push(move)
                        json_file.write(json.dumps({"messages" : [{"role" : "system", "content" : f"{winner} won the following chess game"}] + \
                                                    [{ "role" : role_of_index(i), "content" : move} for i, move in enumerate(moves)]}, ensure_ascii=False))
                        json_file.write('\n')
                    except Exception as e:
                        print(f"Error processing game in {pgn_file}: {e}")
                        continue

    
with tqdm(total=total_files, unit="file") as pbar:  
    with Pool(processes=8) as pool:
        for _ in pool.imap_unordered(process_file, pgn_files):
            pbar.update(1)
