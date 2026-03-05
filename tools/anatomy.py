import sys
from collections import defaultdict

"""
usage: "python anatomy.py <asm_filename>"

Creates a table in asm_filename that shows the different types of instructions present in the compiled file for all instructions defined by twig ISA.
"""

ISA = {

    "r-type": ["add", "sub", "mul", "div", "and", "or", "xor", "slt", "sltu", "addf", "subf", "mulf", "divf", "sll", "srl", "sra"],

    "i-type": ["addi", "subi", "xori", "ori", "slti", "sltiu", "slli", "srli", "srai", "lw", "lh", "lb", "jalr"],

    "f-type": ["isqrt", "sin", "cos", "itof", "ftoi"],

    "s-type": ["sw", "sh", "sb"],

    "b-type": ["beq", "bne", "bge", "bgeu", "blt", "bltu", "beqf", "bnef", "bgef", "bltf"],

    "u-type": ["auipc", "lli", "lmi", "lui"],

    "CSR": ["csrr"],

    "j-type": ["jal"],

    "p-type": ["jpnz", "prr", "prw"],

    "Halt": ["halt"]
}

# Flatten lookup for quick classification
INSTR_TO_TYPE = {}
for instr_type, instructions in ISA.items():
    for instr in instructions:
        INSTR_TO_TYPE[instr] = instr_type


def count_instructions(filename):
    counts = defaultdict(int)

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            # Skip assembler directives (.section, .globl, etc.)
            if line.startswith("."):
                continue

            instr = line.split()[0].lower()

            if instr in INSTR_TO_TYPE:
                counts[instr] += 1
            else:
                # silently ignore non-ISA tokens (labels etc.)
                continue

    return counts


def write_table(counts, output_file):
    with open(output_file, "w") as out:

        total_instr = 0

        #out.write("instr_type, instruction, count\n")
        #out.write("\n")
        #out.write("--------------------------------------------------\n")

        for instr_type in ISA:

            type_total = 0
            out.write(f"{instr_type}\n\n")

            for instr in ISA[instr_type]:
                count = counts[instr]  # 0 if not present
                type_total += count
                out.write(f"{instr} - {count}\n")

            out.write(f"\n{type_total}\n")
            out.write("--------------------------------------------------\n")

            total_instr += type_total

        out.write(f"\n\ntotal instr count = {total_instr}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python anatomy.py f.out")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "anatomy.out"

    counts = count_instructions(input_file)
    write_table(counts, output_file)

    print(f"Results written to {output_file}")


if __name__ == "__main__":
    main()
