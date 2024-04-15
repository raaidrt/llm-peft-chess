import wget
import os
import patoolib
import chess.pgn
import io
import json
from tqdm import tqdm

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

def process_file(game, json_file):
    moves = []
    board = chess.Board()
    for num, move in enumerate(game.mainline_moves(), start=1):
        moves.append(f"{num}. {board.san(move)}")
        board.push(move)
    json_file.write(json.dumps({"moves" : [{ "agent" : move } for move in moves]}, ensure_ascii=False))

    
with io.open('chessdata.json', 'w', encoding='utf-8') as json_file:
    with tqdm(total=total_files, unit="file") as pbar:
        for file_name in pgn_files:
            pgn_file = os.path.join(extract_dir, file_name)
            with open(pgn_file, encoding='latin-1') as pgn:
                while game := chess.pgn.read_game(pgn):
                    process_file(game, json_file)
            pbar.update(1)

print(f"Extracted {len(games)} games from the dataset.")