from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from tqdm import tqdm
from setup_chess_tokenizer import setup_chess_tokenizer, apply_chat_template
from typing import List
import chess
# import chess.engine

# STOCKFISH = "/home/mdhamank/testing/final/llm-peft-chess/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"
# engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)

# NAME = "/data/models/Mistral-7B-Instruct-v0.1/"
# NAME = "mistralai/Mistral-7B-v0.1"
NAME = "data/chess-llm-simple"
# NAME = "data/chess-llm-fen"
# NAME = "data/chess-llm-large"
# RESULTS = "results/results_baseline.json"
# RESULTS = "results/results_qlora_simple.json"
# RESULTS = "results/results_qlora_fen.json"
# RESULTS = "results/results_qlora_large_retry.json"
RESULTS = "results/results_qlora_simple_retry.json"

DATA = "prompts/prompts_test_sft.json"
# DATA = "prompts_large/prompts_test_sft.json"

# tokenizer = AutoTokenizer.from_pretrained("data/chess-llm-simple")
tokenizer = AutoTokenizer.from_pretrained(NAME)
model = AutoModelForCausalLM.from_pretrained(NAME, device_map="auto")
# breakpoint()
model, tokenizer = setup_chess_tokenizer(model, tokenizer)
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token

import re
import json

DATA_SIZE = 100 # how many games to generate

# is_valid(previous_moves, current_move)
# Arguments:
#   previous_moves is a list of moves that came before the current move
#   current_move is the current move that is played
# NOTE: All moves must be presented in the form "1.e4" or "1...e5"
#       If the move is presented in the format "1. e4 e5", then only the first move
#        in the list, which is "e4", will be processed.
def is_valid(previous_moves : List[str], current_move : str) -> bool:
    def cleanup_move(move):
        move = move.split("</s>")[0]
        move = move.split("\n\n")[0]
        move = move.replace("...", ".")
        move = move.strip()
        return move

    def cleanup_move_for_evaluation(move):
        move = cleanup_move(move)
        move = move.split(".")[1]
        move = move.split()[0]
        return move

    # Push all previous moves
    board = chess.Board()
    for move in previous_moves:
        board.push_san(cleanup_move_for_evaluation(move))

    try:
        board.push_san(cleanup_move_for_evaluation(current_move))
        return True
    except Exception as e:
        print("retry move " + str(len(previous_moves)))
        return False

def message_to_moves(message):
    return [m['content'] for m in message]

def evaluate_move(move, game):
    # evaluate the move
    return 0

def generate_chat(messages):
    return {"messages": messages}

def extract_end(response, input_text):
    end = response[len(input_text)+3:]
    r = re.compile(r"\d{1,}\.{1,3}")
    # return the string including and 5 characters after the first regex match
    m = r.search(end)
    if m:
        return end[m.start():m.end()+5]
    else:
        return end
    

def extract_move(response, input_text):
    # extract the move from the response
    # return the string after "|>" and before the last "<|board|>"
    # board_idx = response.rfind("<|board|>")
    board_idx = response.rfind(" [")
    # board_idx = response.rfind(" [b")
    prev_idx = response.rfind("] ", 0, board_idx)
    return response[prev_idx+2:board_idx]

# get first DATA_SIZE games from the test set
data = []
with open(DATA, "r") as f:
    num_lines_done = 0
    for line in f: 
        if num_lines_done >= DATA_SIZE: break 
        num_lines_done += 1
        data.append(line)
        
full_games = [] # list of games, each game is a list of messages
prefixes = [] # list of ongoing games as chat strings
max_moves = 0
moveIdx = 1
prev_responses = [[]]
for line in data: 
    game = json.loads(line)
    messages = game["messages"]
    full_games.append(messages)
    if len(messages) > max_moves:
        max_moves = len(messages)
    # prefixes.append([messages[0]]) # "White won...", "<|white|> 1.e4"
    # prev_responses[0].append(messages[0]['content'])

generated_valid_games = []
generated_valid_games = json.loads(open(RESULTS, "r").read())
startGameIdx = len(generated_valid_games)
print("Starting from game", startGameIdx)
for gameIdx in range(startGameIdx, len(full_games)):
    print("Game", gameIdx)
    message = full_games[gameIdx]
    currGame = [message[0]['content']]
    for moveIdx in range(len(message)):
        text = generate_chat(message[:moveIdx+1])
        text = apply_chat_template(text, tokenizer, "chess-generate", bot_side=['white', 'black'][moveIdx % 2])
        text = text["text"]
        isValid = False
        tempAdd = 0
        while not isValid:
            input = tokenizer(text, return_tensors="pt", padding=True).to(model.device)
            outputs = model.generate(**input, max_new_tokens=9, do_sample=True, temperature=0.2+tempAdd, pad_token_id=tokenizer.eos_token_id) 
            outputs = tokenizer.batch_decode(outputs, skip_special_tokens=False)
            new_move = extract_move(outputs[0], text)
            print(new_move)
            if moveIdx == 0:
                moves = []
            else:
                moves = message_to_moves(message[1:moveIdx+1])
            isValid = is_valid(moves, new_move)
            tempAdd += 0.1
            if tempAdd > 0.8:
                new_move = "invalid"
                break
        currGame.append(new_move)
    generated_valid_games.append(currGame)
    with open(RESULTS, "w") as f:
        json.dump(generated_valid_games, f)
    
    print(moveIdx, ['white', 'black'][moveIdx % 2])


        
        

# while moveIdx < max_moves:
#     new_moves = []
#     for gameIdx, message in enumerate(full_games):
#         if len(message) > moveIdx:
#             text = generate_chat(message[:moveIdx]) # this resets game to ground truth every move
#             text = apply_chat_template(text, tokenizer, "chess-generate", bot_side=['black', 'white'][moveIdx % 2])
#             text = text["text"]
#             prefixes[gameIdx] = text 
#             # should be integrating the model's responses into the game, but that requires some good regex
#             # something something prev_responses[gameIdx])
#         else:
#             prefixes[gameIdx] = apply_chat_template(generate_chat(message), tokenizer, "chess-generate", bot_side=['black', 'white'][moveIdx % 2])["text"]
#     # generate the next move for each game
#     isValid = False
#     while not isValid:
#         batch = prefixes
#         input = tokenizer(batch, return_tensors="pt", padding=True).to(model.device)\
#         # figure out what params to use here
#         outputs = model.generate(**input, max_new_tokens=9, do_sample=True, temperature=0.2, pad_token_id=tokenizer.eos_token_id) 
#         # print(input, outputs[0])
#         # decode the return sequences
#         outputs = tokenizer.batch_decode(outputs, skip_special_tokens=False)

#         # if i == 0:
#         #     # print("batch")
#         #     print("INPUT", batch[0])
#         #     # print("output")
#         #     print("OUTPUT", outputs[0])
#         if NAME == "/data/models/Mistral-7B-Instruct-v0.1/":
#             new_moves_batch = [extract_end(response, text) for response, text in zip(outputs, batch)]
#         else: 
#             new_moves_batch = [extract_move(response, text) for response, text in zip(outputs, batch)]
#         isValid = is_valid(message_to_moves(message[1:moveIdx]), new_moves_batch[0])
#         new_moves.extend(new_moves_batch)
#     prev_responses.append(new_moves)
#     with open(RESULTS, "w") as f:
#         json.dump(prev_responses, f)
    
#     print(moveIdx, ['black', 'white'][moveIdx % 2])
#     moveIdx += 1
#     # if moveIdx >= 10:
#     #     break

# # # save prev_responses to a file
# # with open(RESULTS, "w") as f:
# #     json.dump(prev_responses, f)

