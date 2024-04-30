from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from tqdm import tqdm
from setup_chess_tokenizer import setup_chess_tokenizer, apply_chat_template

# NAME = "/data/models/Mistral-7B-Instruct-v0.2/"
# NAME = "mistralai/Mistral-7B-v0.1"
NAME = "data/chess-llm-simple"
RESULTS = "results/results_qlora_new.json"

DATA = "prompts/prompts_test_sft.json"

tokenizer = AutoTokenizer.from_pretrained(NAME)
model = AutoModelForCausalLM.from_pretrained(NAME, device_map="auto")
# breakpoint()
model, tokenizer = setup_chess_tokenizer(model, tokenizer)

import re
import json

BATCH_SIZE = 8
NUM_RETURN_SEQUENCES = 1
DATA_SIZE = 8 # how many games to generate

def evaluate_move(move, game):
    # evaluate the move
    return 0

def generate_chat(messages):
    return {"messages": messages}

def extract_move(response, input_text):
    # extract the move from the response
    # return the string after "|>" and before the last "<|board|>"
    # board_idx = response.rfind("<|board|>")
    board_idx = response.rfind(" [")
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
moveIdx = 2
prev_responses = []
for line in data: 
    game = json.loads(line)
    messages = game["messages"]
    full_games.append(messages)
    if len(messages) > max_moves:
        max_moves = len(messages)
    prefixes.append(messages[:2]) # "White won...", "<|white|> 1.e4"
    # consider adding more of a prefix when generating from the base model

while moveIdx < max_moves:
    new_moves = []
    for gameIdx, message in enumerate(full_games):
        if len(message) > moveIdx:
            text = generate_chat(message[:moveIdx]) # this resets game to ground truth every move
            text = apply_chat_template(text, tokenizer, "chess-generate", bot_side=['black', 'white'][moveIdx % 2])
            text = text["text"]
            prefixes[gameIdx] = text 
            # should be integrating the model's responses into the game, but that requires some good regex
            # something something prev_responses[gameIdx])
        else:
            prefixes[gameIdx] = apply_chat_template(generate_chat(message), tokenizer, "chess-generate", bot_side=['black', 'white'][moveIdx % 2])["text"]
    # generate the next move for each game
    for i in tqdm(range(0, len(prefixes), BATCH_SIZE)):
        batch = prefixes[i:i+BATCH_SIZE]
        input = tokenizer(batch, return_tensors="pt", padding=True).to(model.device)\
        # figure out what params to use here
        outputs = model.generate(**input, max_new_tokens=9, do_sample=False) 
        # print(input, outputs[0])
        # decode the return sequences
        outputs = tokenizer.batch_decode(outputs, skip_special_tokens=False)

        # if i == 0:
        #     # print("batch")
        #     print("INPUT", batch[0])
        #     # print("output")
        #     print("OUTPUT", outputs[0])
        new_moves_batch = [extract_move(response, text) for response, text in zip(outputs, batch)]
        new_moves.extend(new_moves_batch)
    prev_responses.append(new_moves)
    print(moveIdx, ['black', 'white'][moveIdx % 2])
    moveIdx += 1
    # if moveIdx >= 10:
    #     break

# save prev_responses to a file
with open(RESULTS, "w") as f:
    json.dump(prev_responses, f)

