import argparse
import sys
import struct
import io
from ..api import asm, get_arch

parser = argparse.ArgumentParser(
    description="Twig Tool: ASM, DisASM, and Format Conversion"
)
group = parser.add_mutually_exclusive_group()
group.add_argument("--asm", help="Assemble source file (.s)", metavar="FILE")
group.add_argument(
    "--disasm", help="Disassemble file (.hex, .bin, .oj)", metavar="FILE"
)

# Standalone input for conversion (optional positional argument)
parser.add_argument(
    "input_file", nargs="?", help="Input file for standalone conversion"
)

# Output Format Flags
parser.add_argument(
    "--hex",
    action="store_true",
    help="Output as 8-char hex strings (e.g. 001FE5D3)",
)
parser.add_argument(
    "--bit",
    action="store_true",
    help="Output as 32-char binary strings (e.g. 0101...)",
)
parser.add_argument(
    "--bin", action="store_true", help="Output as raw binary bytes"
)

parser.add_argument("-o", "--output", help="Output filename")

arch = get_arch("twig")


def tool(args=None):
    args = parser.parse_args(args)
    if args.asm:
        do_asm(args)
    elif args.disasm:
        do_disasm(args)
    elif args.input_file:
        do_convert(args.input_file, args)
    else:
        parser.print_help()


def bit_str_to_bytes(filename):
    """
    Reads a text file, filters out everything except '0' and '1',
    and converts the resulting bitstream into raw bytes (Little Endian words).
    """
    try:
        with open(filename, "r") as f:
            # Remove all whitespace and newlines, keep only 0 and 1
            content = "".join(c for c in f.read() if c in "01")

        data = bytearray()
        # Process in 32-bit chunks (Twig word size)
        for i in range(0, len(content), 32):
            word_str = content[i : i + 32]
            if not word_str:
                break
            # Pad to 32 bits if the last segment is shorter
            if len(word_str) < 32:
                word_str = word_str.ljust(32, "0")

            # Convert bit-string to int and pack as Little Endian
            val = int(word_str, 2)
            data.extend(struct.pack("<I", val))
        return data
    except Exception as e:
        print(f"Error parsing bit string file: {e}")
        sys.exit(1)


def bytes_to_hex_str(data):
    """Converts bytes to a list of 8-character Hex strings."""
    lines = []
    # Ensure 4-byte alignment
    pad = len(data) % 4
    if pad != 0:
        data += b"\x00" * (4 - pad)

    for i in range(0, len(data), 4):
        chunk = data[i : i + 4]
        val = int.from_bytes(chunk, byteorder="little")
        lines.append(f"{val:08X}")
    return lines


def bytes_to_bit_str(data):
    """Converts bytes to a list of 32-character binary strings (0101...)."""
    lines = []
    pad = len(data) % 4
    if pad != 0:
        data += b"\x00" * (4 - pad)

    for i in range(0, len(data), 4):
        chunk = data[i : i + 4]
        val = int.from_bytes(chunk, byteorder="little")
        lines.append(f"{val:032b}")
    return lines


def do_convert(input_file, args):
    """Handles format conversion between Bin, Bit-strings, and Hex-strings."""
    print(f"Converting {input_file}...")

    # 1. Read Input (Detect if it's a bit-string text file or raw binary)
    # Usually .hex or .txt in this project refers to '0101' text
    if input_file.endswith(".hex") or input_file.endswith(".txt"):
        raw_data = bit_str_to_bytes(input_file)
    else:
        with open(input_file, "rb") as f:
            raw_data = f.read()

    # 2. Generate Output based on flags
    if args.hex:
        # Output actual Hex (e.g., 001FE5D3)
        out_name = args.output if args.output else "output.hex"
        lines = bytes_to_hex_str(raw_data)
        with open(out_name, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Hexadecimal strings written to {out_name}")

    elif args.bit:
        # Output Bit-strings (e.g., 0101...)
        out_name = args.output if args.output else "output.bit"
        lines = bytes_to_bit_str(raw_data)
        with open(out_name, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Binary strings (0101) written to {out_name}")

    elif args.bin:
        # Output Raw Binary
        out_name = args.output if args.output else "output.bin"
        with open(out_name, "wb") as f:
            f.write(raw_data)
        print(f"Raw binary written to {out_name}")
    else:
        print("Error: Please specify output format (--hex, --bit, or --bin)")
        sys.exit(1)


def do_asm(args):
    """Assembles and outputs in the requested format."""
    print(f"Assembling {args.asm}...")
    try:
        with open(args.asm, "r") as f:
            obj = asm(f, arch)
    except Exception as e:
        print(f"Assembly failed: {e}")
        sys.exit(1)

    image = obj.get_image("code") or (obj.images[0] if obj.images else None)
    raw_data = image.data if image else b""

    if args.hex:
        lines = bytes_to_hex_str(raw_data)
        with open(args.output or "a.out.hex", "w") as f:
            f.write("\n".join(lines) + "\n")
    elif args.bit:
        lines = bytes_to_bit_str(raw_data)
        with open(args.output or "meminit.hex", "w") as f:
            f.write("\n".join(lines) + "\n")
    elif args.bin:
        with open(args.output or "a.out.bin", "wb") as f:
            f.write(raw_data)
    else:
        obj.save(open(args.output or "a.out.oj", "w"))


def do_disasm(args):
    """Handles disassembly with a robust fallback for
    JAL/Label instructions."""
    filename = args.disasm
    print(f"Disassembling {filename}...")

    from ..api import get_arch

    arch = get_arch("twig")
    raw_data = b""

    # 1. Input detection (Same as before)
    is_hex_input = args.hex or filename.endswith(".hex")
    is_obj_input = filename.endswith(".oj")

    if is_hex_input:
        raw_data = bit_str_to_bytes(filename)
    elif is_obj_input:
        # ... object file loading logic ...
        pass
    else:
        with open(filename, "rb") as f:
            raw_data = f.read()

    print(f"{'Addr':<8} | {'Hex':<8} | {'Instruction'}")
    print("-" * 50)

    f_stream = io.BytesIO(raw_data)
    addr = 0

    while f_stream.tell() < len(raw_data):
        chunk = f_stream.read(4)
        if len(chunk) < 4:
            break

        val = int.from_bytes(chunk, byteorder="little")
        decoded_ins = None

        # --- Standard PPCI Decoding ---
        for instruction_def in arch.isa.instructions:
            try:
                decoded_ins = instruction_def.decode(chunk)
                if decoded_ins:
                    break
            except Exception:
                continue

        # --- Display Logic with Fallback ---
        if decoded_ins:
            print(f"{addr:08X} | {val:08X} | {decoded_ins}")
        else:
            # Manually extract opcode (lowest 7 bits)
            opcode = val & 0x7F

            # 0x60 is the opcode for 'Bl' (jal) in Twig
            if opcode == 0x60:
                # Based on TwigJToken: rd (7-13), imm (13-30)
                rd_idx = (val >> 7) & 0x3F
                # 17-bit immediate value
                imm_val = (val >> 13) & 0x1FFFF

                # Sign extension for 17-bit
                if imm_val & 0x10000:
                    imm_val -= 0x20000

                print(f"{addr:08X} | {val:08X} | jal x{rd_idx}, {imm_val}")
            else:
                # If still unknown, output as data
                print(f"{addr:08X} | {val:08X} | dd {val}")

        addr += 4


if __name__ == "__main__":
    sys.exit(tool())
