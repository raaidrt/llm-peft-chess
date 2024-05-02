from tqdm import tqdm
import random

# SAMPLES = 10000
# SAMPLES = 4437

with open('chessdata_large.json', 'r') as f:
    lines = f.readlines()
    new_lines = []
    with tqdm(total=len(lines), unit="line") as pbar:
        for line in tqdm(lines, total = len(lines)):
            # line = line.replace("agent", "user")
            # assistant_index = line.index("assistant")
            # user_index = line.index("user")
            # if assistant_index < user_index:
            #     line = line.replace("assistant", 'user", "content": "pass"}, {"role": "assistant', 1)
            # else:
            #     line = line
            # line = line[:83] + "{\"role\": \"assistant\", \"content\": \"Make a move or pass\"}, " + line[83:]
            # line = line.replace("system", "user", 1)
            new_lines.append(line)
            pbar.update(1)
    lines = new_lines
    # lines = random.choices(lines, k=SAMPLES)
    num_lines = len(lines)
    num_train = int(num_lines * 0.8)
    train_lines = lines[:num_train]
    test_lines = lines[num_train:]

    with open('prompts_large/prompts_train_sft.json', 'w') as train_file:
        train_file.writelines(train_lines)
    with open('prompts_large/prompts_test_sft.json', 'w') as test_file:
        test_file.writelines(test_lines)
    