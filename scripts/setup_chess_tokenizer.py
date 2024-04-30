from typing import Tuple, Literal
from transformers import PreTrainedModel, PreTrainedTokenizer
from alignment.data import maybe_insert_system_message, is_openai_format

def setup_chess_tokenizer( model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> Tuple[PreTrainedModel, PreTrainedTokenizer]:
    tokenizer.add_special_tokens({"additional_special_tokens": ['<|white|>', '<|black|>', '<|board|>']})
    # set chat format for tokenizer
    # tokenizer.chat_template = "{% for message in messages %}\n{% if message['role'] == 'system' %}\n{{ message['content'] + eos_token }}\n{% elif message['role'] == 'user' %}\n{{ '<|white|> ' + message['content'] + ' <|board|> ' + message['fen'] }}\n{% elif message['role'] == 'assistant' %}\n{{ '<|black|> ' + message['content'] + ' <|board|> ' + message['fen'] }}\n{% endif %}\n{% if loop.last and add_generation_prompt %}\n{{ '<|' + add_generation_prompt + '|>' }}\n{% endif %}\n{% endfor %}"
    tokenizer.chat_template = "{% for message in messages %}{% if message['role'] == 'system' %}{{ message['content'] + eos_token }}{% elif message['role'] == 'user' %}{{ '<|white|> ' + message['content'] }}{% elif message['role'] == 'assistant' %}{{ '<|black|> ' + message['content'] }}{% endif %}{% if loop.last and add_generation_prompt %}{{ '<|' + add_generation_prompt + '|>' }}{% endif %}{% endfor %}"
    tokenizer.padding_side = "left"
    # resize embedding layer to a multiple of 64, https://x.com/karpathy/status/1621578354024677377
    # pad_to_multiple_of=64
    model.resize_token_embeddings(
        len(tokenizer), pad_to_multiple_of=None
    )
    # Update the model config to use the new eos & bos tokens
    if getattr(model, "config", None) is not None:
        model.config.pad_token_id = tokenizer.unk_token
    # Update the generation config to use the new eos & bos token
    if getattr(model, "generation_config", None) is not None:
        # model.generation_config.pad_token_id = tokenizer.unk_token
        model.generation_config.additional_special_tokens = tokenizer.additional_special_tokens

    return model, tokenizer

def apply_chat_template(
    example,
    tokenizer,
    task: Literal["sft", "generation", "rm", "dpo", "chess-generate"],
    auto_insert_empty_system_msg: bool = True,
    bot_side: Literal["white", "black"] = "black"
):
    if task in ["sft", "generation", "chess-generate"]:
        messages = example["messages"]
        # We add an empty system message if there is none
        if auto_insert_empty_system_msg:
            maybe_insert_system_message(messages, tokenizer)
        if task == "chess-generate":
            example["text"] = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=bot_side,
            )
        else:
            example["text"] = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True if task == "generation" else False,
            )
    elif task == "rm":
        if all(k in example.keys() for k in ("chosen", "rejected")):
            chosen_messages = example["chosen"]
            rejected_messages = example["rejected"]
            # We add an empty system message if there is none
            if auto_insert_empty_system_msg:
                maybe_insert_system_message(chosen_messages, tokenizer)
                maybe_insert_system_message(rejected_messages, tokenizer)

            example["text_chosen"] = tokenizer.apply_chat_template(chosen_messages, tokenize=False)
            example["text_rejected"] = tokenizer.apply_chat_template(rejected_messages, tokenize=False)
        else:
            raise ValueError(
                f"Could not format example as dialogue for `rm` task! Require `[chosen, rejected]` keys but found {list(example.keys())}"
            )
    elif task in ["dpo", "orpo"]:
        if all(k in example.keys() for k in ("chosen", "rejected")):
            if not is_openai_format(example["chosen"]) or not is_openai_format(example["rejected"]):
                raise ValueError(
                    f"Could not format example as dialogue for `{task}` task! Require OpenAI format for all messages"
                )

            # For DPO/ORPO, the inputs are triples of (prompt, chosen, rejected), where `chosen` and `rejected` are the final turn of a dialogue
            # We therefore need to extract the N-1 turns to form the prompt
            if "prompt" in example and is_openai_format(example["prompt"]):
                prompt_messages = example["prompt"]
                chosen_messages = example["chosen"]
                rejected_messages = example["rejected"]
            else:
                prompt_messages = example["chosen"][:-1]
                # Now we extract the final turn to define chosen/rejected responses
                chosen_messages = example["chosen"][-1:]
                rejected_messages = example["rejected"][-1:]

            # Prepend a system message if the first message is not a system message
            if auto_insert_empty_system_msg:
                maybe_insert_system_message(prompt_messages, tokenizer)

            example["text_prompt"] = tokenizer.apply_chat_template(prompt_messages, tokenize=False)
            example["text_chosen"] = tokenizer.apply_chat_template(chosen_messages, tokenize=False)
            example["text_rejected"] = tokenizer.apply_chat_template(rejected_messages, tokenize=False)
        else:
            raise ValueError(
                f"Could not format example as dialogue for `{task}` task! Require either the "
                f"`[chosen, rejected]` or `[prompt, chosen, rejected]` keys but found {list(example.keys())}"
            )
    else:
        raise ValueError(
            f"Task {task} not supported, please ensure that the provided task is one of ['sft', 'generation', 'rm', 'dpo', 'orpo']"
        )
    return example