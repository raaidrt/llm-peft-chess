from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from tqdm import tqdm
from setup_chess_tokenizer import setup_chess_tokenizer, apply_chat_template
from typing import List, Literal
import chess
# import chess.engine

# STOCKFISH = "/home/mdhamank/testing/final/llm-peft-chess/stockfish/stockfish-ubuntu-x86-64-sse41-popcnt"
# engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)

import re
import json
import sys


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
# is_valid(previous_moves, current_move)
# Arguments:
#   previous_moves is a list of moves that came before the current move
#   current_move is the current move that is played
# NOTE: All moves must be presented in the form "1.e4" or "1...e5"
#       If the move is presented in the format "1. e4 e5", then only the first move
#        in the list, which is "e4", will be processed.
def is_valid(previous_moves : List[str], current_move : str) -> bool:

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

def main(version : Literal["simple","large"] = "large"):
    if version == "simple":
        NAME = "data/chess-llm-simple"
        RESULTS = "results/simple_game_log.json"
    elif version == "large":
        NAME = "data/chess-llm-large"
        RESULTS = "results/large_game_log.json"
    tokenizer = AutoTokenizer.from_pretrained(NAME)
    model = AutoModelForCausalLM.from_pretrained(NAME, device_map="auto")
    # breakpoint()
    model, tokenizer = setup_chess_tokenizer(model, tokenizer)
    tokenizer.padding_side = "left"
    tokenizer.pad_token = tokenizer.eos_token

    mode = int(input("Enter game mode (0 - bot plays white, 1 - bot plays black, 2 - ask each move): "))
    board = chess.Board()
    game = []
    messages = []
    if mode == 0 or mode == 2:
        messages.append({"role": "system", "content": "white won the following chess game"})
    else:
        messages.append({"role": "system", "content": "black won the following chess game"})

    while not board.is_game_over():
        bot_turn = False
        move = None
        if mode == 2: 
            move = input("> ")
            if move == "n":
                bot_turn = True
        elif mode == 0:
            bot_turn = board.turn == chess.WHITE
        elif mode == 1:
            bot_turn = board.turn == chess.BLACK
        if bot_turn:
            text = generate_chat(messages)
            text = apply_chat_template(text, tokenizer, "chess-generate", bot_side=['white', 'black'][len(game) % 2])
            text = text["text"]
            intok = tokenizer(text, return_tensors="pt", padding=True).to(model.device)
            notvalid = True
            tempAdd = 0
            while notvalid:
                outputs = model.generate(**intok, max_new_tokens=9, do_sample=True, temperature=0.2, pad_token_id=tokenizer.eos_token_id) 
                outputs = tokenizer.batch_decode(outputs, skip_special_tokens=False)
                new_move = extract_move(outputs[0], text)
                print(new_move)
                notvalid = False
                try:
                    board.push_san(cleanup_move_for_evaluation(new_move))
                except Exception as e:
                    notvalid = True
                    tempAdd += 0.1
                    if tempAdd > 0.8:
                        new_move = input("I'm lost, please help me: ")
                        board.push_san(cleanup_move_for_evaluation(new_move))
                        break
                    
            if board.turn == chess.BLACK:
                messages.append({"role": "user", "content": new_move})
            else:
                messages.append({"role": "assistant", "content": new_move})
            game.append(new_move)
        else:
            if move is None:
                move = input("Enter move: ")
            if board.turn == chess.WHITE:
                messages.append({"role": "user", "content": move})
            else:
                messages.append({"role": "assistant", "content": move})
            board.push_san(cleanup_move_for_evaluation(move))
            game.append(move)

        print(board)
    print("Game over")
    print(board.result())
    with open(RESULTS, "w") as f:
        json.dump(game, f)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()