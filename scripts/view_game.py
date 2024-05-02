import json
DATA = "prompts/prompts_train_sft.json"

# get first game

data = []
with open(DATA, "r") as f:
    print(len(list(f)))
#     for line in f:
#         data.append(json.loads(line))
#         break

# for game in data:
#     for message in game["messages"]:
#         print(message["content"])
#     print()
