# # split chessdata.json into train and test files
# # each line is a json object

# with open('chessdata.json', 'r') as f:
#     lines = f.readlines()
#     num_lines = len(lines)
#     num_train = int(num_lines * 0.8)
#     train_lines = lines[:num_train]
#     test_lines = lines[num_train:]

#     with open('prompts/prompts_train_sft.json', 'w') as train_file:
#         train_file.writelines(train_lines)
#     with open('prompts/prompts_test_sft.json', 'w') as test_file:
#         test_file.writelines(test_lines)
    
# # replace all occurances of "agent" with "user" in prompts_train_sft.json
# with open('prompts/prompts_train_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = [line.replace('"agent"', '"user"') for line in lines]
#     with open('prompts/prompts_train_sft.json', 'w') as f:
#         f.writelines(new_lines)

# # replace all occurances of "agent" with "user" in prompts_test_sft.json
# with open('prompts/prompts_test_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = [line.replace('"agent"', '"user"') for line in lines]
#     with open('prompts/prompts_test_sft.json', 'w') as f:
#         f.writelines(new_lines)

# # if the word 'assistant' comes before 'user' in a line, insert "hello" before the word 'assistant'
# with open('prompts/prompts_train_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = []
#     for line in lines:
#         assistant_index = line.index("assistant")
#         user_index = line.index("user")
#         if assistant_index < user_index:
#             new_lines.append(line.replace("assistant", "user', 'content': 'pass'}, {'role': 'assistant", 1))
#         else:
#             new_lines.append(line)
#     with open('prompts/prompts_train_sft.json', 'w') as f:
#         f.writelines(new_lines)

# with open('prompts/prompts_test_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = []
#     for line in lines:
#         assistant_index = line.index("assistant")
#         user_index = line.index("user")
#         if assistant_index < user_index:
#             new_lines.append(line.replace("assistant", "user', 'content': 'pass'}, {'role': 'assistant", 1))
#         else:
#             new_lines.append(line)
#     with open('prompts/prompts_test_sft.json', 'w') as f:
#         f.writelines(new_lines)

# with open('prompts/prompts_train_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = []
#     for line in lines:
#         line = line[:83] + "{\"role\": \"assistant\", \"content\": \"Make a move or pass\"}, " + line[83:]
#         line = line.replace("system", "user", 1)
#         new_lines.append(line)
#     print(new_lines[0])
#     with open('prompts/prompts_train_sft.json', 'w') as f:
#         f.writelines(new_lines)

# with open('prompts/prompts_test_sft.json', 'r') as f:
#     lines = f.readlines()
#     new_lines = []
#     for line in lines:
#         line = line[:83] + "{\"role\": \"assistant\", \"content\": \"Make a move or pass\"}, " + line[83:]
#         line = line.replace("system", "user", 1)
#         new_lines.append(line)
#     with open('prompts/prompts_test_sft.json', 'w') as f:
#         f.writelines(new_lines)

# with open('prompts/prompts_test_sft.json', 'r') as f:
#     lines = f.readlines()
#     print(lines[0])

with open('prompts/prompts_train_sft.json', 'r') as f:
    lines = f.readlines()
    new_lines = [line.replace("'", '"', 8) for line in lines]
    with open('prompts/prompts_train_sft.json', 'w') as f:
        f.writelines(new_lines)

with open('prompts/prompts_test_sft.json', 'r') as f:
    lines = f.readlines()
    new_lines = [line.replace("'", '"', 8) for line in lines]
    with open('prompts/prompts_test_sft.json', 'w') as f:
        f.writelines(new_lines)