# En PEFT-ssant 
Read our [paper](https://typst.app/project/rbiWDPjgVid-_OGyj0-zkM)

## Poster
![poster image](https://github.com/raaidrt/llm-peft-chess/blob/main/poster.png?raw=true)

## Code Explanation
The first part of our code converts the Kingbase dataset into a JSON file with individual chess moves. We take this file and further process it along with splitting it up into testing and training sets. We then used HuggingFace Alignment Handbook as a template to fine tune the Mistral 7B model. We created a Jinja chat template to apply to each data point. We adjusted several parameters such as LoRA alpha and r, number of epochs, and packing. For evaluation we wrote a loop to simulate 100 games from the test set in parallel. The model would come up with a next move suggestion for every game given a prefix of moves. We had to stop evaluation at 100 moves per game since execution time is quadratic with sequence length and running 100 games at a time was computationally expensive. We wrote code to make the model retry generating if a move is invalid. Rerunning evaluations with a maximum of 8 retries per move, we were able to calculate how much worse our models performed per move compared to StockFish. 

## Setup
Follow setup instructions from [Huggingface Alignment Handbook](https://github.com/huggingface/alignment-handbook). We used torch==2.2.2 and flash-attn==2.5.2.
## Creating the dataset
Run ``dataparser/chess/extract.py`` and ``dataparser/chess/split_data.py`` to create ``chessdata.json`` and a prompts folder with the test and train data.
## Fine-tuning the Model
Edit and run ``scripts/launch.sh`` depending on how many GPUs you have and which sft recipe you want.
Extract the zip files in the data folder to use the models we fine tuned.
## Generating Moves
Run ``scripts/generate_new.py`` or ``scripts/generate_retry.py`` to generate only valid moves
## Evaluating Results
Use scripts in ``evaluate_results``
## Play a game
Run ``scripts/play_chess.py`` to play a game with the bot. Mode 0 and 1 have the bot play white and black. Mode 2 asks you each move to either input a move or press 'n' to have the bot play. Human inputs must be in the form of '1.e4' or '1...e5' and must be valid moves.
