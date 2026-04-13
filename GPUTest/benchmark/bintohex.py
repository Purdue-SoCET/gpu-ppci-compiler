import sys
from pathlib import Path

def convert_file(input_path, output_path):
    print(f"Reading: {input_path}")

    try:
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
                parts = line.strip().split()

                # Make sure the line has both an address and data
                if len(parts) == 2:
                    addr_str = parts[0]
                    bin_str = parts[1]

                    # Convert the 32-bit binary string to an integer, then format it as 8-character hex
                    try:
                        hex_val = f"{int(bin_str, 2):08X}"
                        outfile.write(f"{addr_str} {hex_val}\n")
                    except ValueError:
                        print(f"Skipping invalid binary data at {addr_str}: {bin_str}")

        print(f"Success! Saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: Could not find the input file '{input_path}'")

# --- Configuration ---
# Change these filenames to match your exact files
INPUT_FILE = "build/pixelInput_memDump_1024.txt"
OUTPUT_FILE = "build/pixelInput_memDump_1024_HEX.txt"

if __name__ == "__main__":
    convert_file(INPUT_FILE, OUTPUT_FILE)
