#!/bin/bash

python dataparser/chess/extract.py

# Set the input and output file paths
input_folder="data"
output_file="chessdata.json"

# Remove the output file if it already exists
rm -f "$output_file"

# Concatenate all JSON files in the input folder and write to the output file
cat "$input_folder"/*.json > "$output_file"

rm -f "$input_folder"/*.json

echo "Concatenation complete. Output file: $output_file"