import sys
import argparse
from typing import Dict, List

# Default values for special operands
DEFAULT_PRED = 0
DEFAULT_START = 0
DEFAULT_END = 1

def int_to_bin(value: int, bits: int) -> str:
    """Converts a signed integer to a two's complement binary string of a specific bit width."""
    if value >= 0:
        return format(value, f'0{bits}b')
    else:
        # For negative numbers, calculate two's complement
        return format((1 << bits) + value, f'0{bits}b')

def parse_register(reg_str: str) -> int:
    """Parses a register string like 'x10' or a CSR string like 'x1000' into its integer value."""
    if reg_str.lower().startswith('x'):
        try:
            return int(reg_str[1:])
        except ValueError:
            raise ValueError(f"Invalid register format: {reg_str}")
    raise ValueError(f"Expected register format 'x##', but got: {reg_str}")

def parse_pred_register(reg_str: str) -> int:
    """Parses a predicate register string like 'p10' into its integer value."""
    if reg_str.lower().startswith('p'):
        try:
            return int(reg_str[1:])
        except ValueError:
            raise ValueError(f"Invalid register format: {reg_str}")
    raise ValueError(f"Expected register format 'p##' but got {reg_str}")

def load_opcodes(filepath: str) -> Dict[str, str]:
    """Loads opcode definitions from a file into a dictionary."""
    opcodes = {}
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                if len(parts) == 2:
                    opcodes[parts[0]] = parts[1]
    return opcodes

def assemble(input_file: str, output_file: str, opcodes: Dict[str, str]):
    """
    Assembles the given .s file into binary machine code using a two-pass approach.
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # --- First Pass: Build the symbol table for labels ---
    symbol_table = {}
    pc = 0
    for line in lines:
        clean_line = line.split('#')[0].strip() # Remove comments and whitespace
        if not clean_line:
            continue

        if ':' in clean_line:
            label = clean_line.split(':')[0].strip()
            symbol_table[label] = pc
            instruction_part = clean_line.split(':')[1].strip()
            if instruction_part:
                pc += 4
        else:
            pc += 4

    # --- Second Pass: Generate machine code ---
    pc = 0
    machine_code = []
    for line_num, line in enumerate(lines, 1):
        clean_line = line.split('#')[0].strip().replace(',', ' ')
        if ':' in clean_line:
            clean_line = clean_line.split(':')[1].strip()

        if not clean_line:
            continue

        parts = clean_line.split()
        mnemonic = parts[0]
        operands = parts[1:]

        if mnemonic not in opcodes:
            raise ValueError(f"Error on line {line_num}: Unknown mnemonic '{mnemonic}'")

        opcode_bin = opcodes[mnemonic]

        # Initialize binary fields
        rd_bin, rs1_bin, rs2_bin = '000000', '000000', '000000'
        pred_bin = int_to_bin(DEFAULT_PRED, 5)
        start_bin = str(DEFAULT_START)
        end_bin = str(DEFAULT_END)

        # Instruction type definitions
        R_TYPE = ['add', 'sub', 'mul', 'div', 'and', 'xor', 'or', 'slt', 'sltu',
                  'addf', 'subf', 'mulf', 'divf', 'sll', 'srl', 'sra']
        LOAD_TYPE = ['lb', 'lh', 'lw']
        STORE_TYPE = ['sb', 'sh', 'sw']
        SINGLE_SRC_TYPE = ['isqrt', 'sin', 'cos', 'itof', 'ftoi']
        I_TYPE = ['addi', 'xori', 'ori', 'slli', 'srli', 'srai', 'slti', 'sltiu']
        BRANCH_TYPE = ['beq', 'bne', 'bge', 'bgeu', 'blt', 'bltu']
        U_TYPE = ['lui', 'lmi', 'lli', 'auipc']
        JALR_TYPE = ['jalr']
        JAL_TYPE = ['jal']
        JPNZ_TYPE = ['jpnz']
        CSR_TYPE = ['csrr', 'csrw']

        try:
            num_primary_operands = 0
            if (mnemonic in R_TYPE or mnemonic in LOAD_TYPE or
                mnemonic in BRANCH_TYPE or mnemonic in I_TYPE or
                mnemonic in JALR_TYPE or mnemonic in JAL_TYPE or
                mnemonic in SINGLE_SRC_TYPE or mnemonic in STORE_TYPE):
                num_primary_operands = 3
            elif mnemonic in U_TYPE or mnemonic in JPNZ_TYPE or mnemonic in CSR_TYPE:
                num_primary_operands = 2

            pred_op_idx = num_primary_operands
            start_op_idx = num_primary_operands + 1
            end_op_idx = num_primary_operands + 2

            if len(operands) > pred_op_idx and operands[pred_op_idx].lower() != "pred":
                pred_bin = int_to_bin(int(operands[pred_op_idx]), 5)
            if len(operands) > start_op_idx and operands[start_op_idx].lower() != "start":
                start_bin = str(int(operands[start_op_idx]))
            if len(operands) > end_op_idx and operands[end_op_idx].lower() != "end":
                end_bin = str(int(operands[end_op_idx]))

            # Parse main operands based on instruction type
            if mnemonic in R_TYPE:
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                rs2 = parse_register(operands[2])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(rs2, 6)

            elif mnemonic in STORE_TYPE:
                rs1 = parse_register(operands[0])
                rs2 = parse_register(operands[1])
                imm = int(operands[2])
                rd_bin = int_to_bin(imm, 6)
                rs1_bin = int_to_bin(rs1,6)
                rs2_bin = int_to_bin(rs2,6)
            elif mnemonic in LOAD_TYPE:
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                imm = int(operands[2])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(imm, 6)

            elif mnemonic in SINGLE_SRC_TYPE:
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(0, 6)

            elif mnemonic in I_TYPE:
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                imm = int(operands[2])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(imm, 6)

            elif mnemonic in BRANCH_TYPE:
                rs1 = parse_register(operands[1])
                rs2 = parse_register(operands[2])
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(rs2, 6)

                rd = parse_pred_register(operands[0])

                rd_bin = int_to_bin(rd, 6)

            elif mnemonic in JALR_TYPE:
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)

                target_str = operands[2]
                if target_str in symbol_table:
                    target_addr = symbol_table[target_str]
                else:
                    target_addr = int(target_str)

                imm = target_addr
                rs2_bin = int_to_bin(imm, 6)

            elif mnemonic in U_TYPE:
                rd = parse_register(operands[0])
                imm = int(operands[1])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(imm & 0x3F, 6)
                rs2_bin = int_to_bin((imm >> 6) & 0x3F, 6)

            elif mnemonic in JAL_TYPE:
                # =================== CHANGE IS HERE ===================
                # Format: jal rd, rs1, imm
                rd = parse_register(operands[0])
                rs1 = parse_register(operands[1])
                rd_bin = int_to_bin(rd, 6)
                rs1_bin = int_to_bin(rs1, 6)

                target_str = operands[2]
                if target_str in symbol_table:
                    target_addr = symbol_table[target_str]
                else:
                    target_addr = int(target_str)

                # Encode the absolute address immediate into the rs2 field
                imm = target_addr
                rs2_bin = int_to_bin(imm & 0x3F, 6) # Mask to 6 bits
                # ======================================================

            elif mnemonic in JPNZ_TYPE:
                rs1 = parse_pred_register(operands[0])
                rs2 = parse_register(operands[1])
                rs1_bin = int_to_bin(rs1, 6)
                rs2_bin = int_to_bin(rs2, 6)

            elif mnemonic in CSR_TYPE:
                if mnemonic == 'csrr':
                    rd = parse_register(operands[0])
                    csr_addr = parse_register(operands[1])
                    rd_bin = int_to_bin(rd, 6)
                    rs1_bin = int_to_bin(csr_addr & 0x3F, 6)
                    rs2_val = (csr_addr >> 6) & 0xF
                    rs2_bin = int_to_bin(rs2_val, 6)
                elif mnemonic == 'csrw':
                    csr_addr = parse_register(operands[0])
                    rs1 = parse_register(operands[1])
                    rs1_bin = int_to_bin(rs1, 6)
                    rd_bin = int_to_bin(csr_addr & 0x3F, 6)
                    rs2_val = (csr_addr >> 6) & 0xF
                    rs2_bin = int_to_bin(rs2_val, 6)

            instruction = f"{end_bin}{start_bin}{pred_bin}{rs2_bin}{rs1_bin}{rd_bin}{opcode_bin}"
            machine_code.append(instruction)

        except (ValueError, IndexError) as e:
            print(f"Error processing line {line_num}: '{line.strip()}'")
            print(f"  -> {e}")
            sys.exit(1)

        pc += 4

    with open(output_file, 'w') as f:
        for code in machine_code:
            f.write(code + '\n')
    print(f"Assembly successful! Output written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="A custom two-pass assembler.")
    parser.add_argument("input_file", help="The input assembly .s file.")
    parser.add_argument("-o", "--output", dest="output_file", default="a.out",
                        help="The output file for the machine code (default: a.out).")
    parser.add_argument("--opcodes", dest="opcodes_file", required=True,
                        help="The file containing the opcode definitions.")
    args = parser.parse_args()

    try:
        opcodes = load_opcodes(args.opcodes_file)
        assemble(args.input_file, args.output_file, opcodes)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
