from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from alignment import apply_chat_template
from tqdm import tqdm

# NAME = "/data/models/Mistral-7B-Instruct-v0.1/"
NAME = "mistralai/Mistral-7B-v0.1"
# NAME = "data/qlora-model-name"
RESULTS = "results/results_1024_90.json"

DATA = "prompts/prompts_test_sft.json"

tokenizer = AutoTokenizer.from_pretrained(NAME)
tokenizer.pad_token = tokenizer.unk_token
# tokenizer.padding_side = "right"
# this should be right I think, but extracting the results is easier with left for some reason
model = AutoModelForCausalLM.from_pretrained(NAME, device_map="auto")

import re
import json

BATCH_SIZE = 64
NUM_RETURN_SEQUENCES = 1
DATA_SIZE = 1024 # how many games to generate
MAX_MOVES = 90 # stop game after this many moves

def evaluate_move(move, game):
    # evaluate the move
    return 0

def generate_chat(messages):
    return {"messages": messages}

def extract_move(response, input_text):
    # extract the move from the response
    # write some regex for this or something
    # find the last instance of "INST" in the response and return the string after it
    return response[response.rfind("[/INST]")+7:]

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
moveIdx = 3
prev_responses = []
for line in data: 
    game = json.loads(line)
    messages = game["messages"]
    full_games.append(messages)
    if len(messages) > max_moves:
        max_moves = len(messages)
        print(max_moves, messages[-1])
    # messages[0]["content"] = "Play a game of chess. Only use pgn notation in your responses." # custom prompt for base model?
    prefixes.append(messages[:3]) # "User: White won...", "Assistant: Make a move or pass", "User: 1.e4"
    # consider adding more of a prefix when generating from the base model

if max_moves > MAX_MOVES:
    max_moves = MAX_MOVES

while moveIdx < max_moves:
    new_moves = []
    for gameIdx, message in enumerate(full_games):
        if len(message) > moveIdx:
            text = generate_chat(message[:moveIdx]) # this resets game to ground truth every move
            text = apply_chat_template(text, tokenizer, "generation")
            text = text["text"]
            prefixes[gameIdx] = text 
            # should be integrating the model's responses into the game, but that requires some good regex
            # something something prev_responses[gameIdx])
        else:
            prefixes[gameIdx] = apply_chat_template(generate_chat(message), tokenizer, "generation")["text"]
    # generate the next move for each game
    for i in tqdm(range(0, len(prefixes), BATCH_SIZE)):
        batch = prefixes[i:i+BATCH_SIZE]
        input = tokenizer(batch, return_tensors="pt", padding=True).to(model.device)
        # figure out what params to use here
        outputs = model.generate(**input, max_new_tokens=10, do_sample=False, temperature=0.0, top_p=1.0) 
        # decode the return sequences
        outputs = tokenizer.batch_decode(outputs, skip_special_tokens=False)

        if i == 0:
            # print("batch")
            # print(batch[0])
            # print("output")
            print(outputs[0])
        new_moves_batch = [extract_move(response, text) for response, text in zip(outputs, batch)]
        new_moves.extend(new_moves_batch)
    prev_responses.append(new_moves)
    print(moveIdx)
    moveIdx += 2
    # if moveIdx >= 10:
    #     break

# save prev_responses to a file
with open(RESULTS, "w") as f:
    json.dump(prev_responses, f)

