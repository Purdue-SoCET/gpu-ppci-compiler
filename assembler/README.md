# Custom ISA Assembler

This is a Python assembler **external from the main compiler** designed for the GPU core custom instruction set (naming undefined). It translates assembly language code written for this specific ISA into 32-bit binary machine code.


## How to Use

To assemble a `.s` file, run the `assembler.py` script from your terminal with the following arguments:

```
python assembler.py <input_file.s> --opcodes <opcodes_file.txt> -o <output_file.bin>
```


## Features

- **Specific Instruction Encoding:** Follows the defined 32-bit format:
  `{end_packet[31], start_packet[30], pred[29:25], rs2[24:19], rs1[18:13], rd[12:7], opcode[6:0]}`.

## Prerequisites

- Python 3.x

### Arguments

- `<input_file.s>`: (Required) The path to the assembly source file you want to assemble.
- `--opcodes <opcodes_file.txt>`: (Required) The path to the text file containing the instruction-to-opcode mappings.
- `-o <output_file.bin>`: (Optional) The desired name for the output binary file. If not provided, it defaults to `a.out`.

### Example

Given `sampleASM.s` and `opcodes.txt`, you can assemble it using the following command:

```
python assembler.py sampleASM.s --opcodes opcodes.txt -o machine_code.bin
```

Upon successful execution, the script will print:

```
Assembly successful! Output written to machine_code.bin
```

and the binary code will be saved in the `machine_code.bin` file.

---

## Assembly Language Syntax

### Instruction Format

Each instruction should be on its own line and generally follows this format:

```
mnemonic operand1, operand2, operand3, ...
```

### Operands

- **Order:** 1 is rd, 2 is rs1, 3 is rs2, 4 is predicate, 5 is packet start, 6 is packet end.
- **Registers:** Standard registers are denoted with an `x` prefix (e.g., `x10`, `x11`). CSR registers can have higher numbers (e.g., `x1000`).
- **Predicate register:** When writing to predicate registers use `p` instead of `x` e.g `p11`
- **Predicate Field:** Written in decimal with no prefix e.g. `30`
- **Labels:** Used as targets for branch and jump instructions (e.g., `branched`).
  A label is defined by placing it on its own line or at the beginning of an instruction line, followed by a colon:

```
my_label:
    add x1, x2, x3
```

### Comments

Comments begin with a `#` character. Anything from the `#` to the end of the line is ignored by the assembler.

```
# This is a comment
add x10, x11, x12 # This is an inline comment
```

---

## Special Operands (`pred`, `start`, `end`)

Instructions should take these three operands at the end of the line.
If these are omitted or specified by name, they will use their default values.

- **pred:** A 5-bit predicate value. Default is `0`.
- **start:** A 1-bit start flag. Default is `0`.
- **end:** A 1-bit end flag. Default is `1`.

### Example Usage:

Other examples are given in `sampleASM.s`

```
# Using default values
add x10, x11, x12

# Explicitly using default values
add x10, x11, x12, pred, start, end

# Using custom values (e.g., pred=5, start=1, end=0)
add x10, x11, x12, 5, 1, 0
```

---

## Opcodes File Format

The `--opcodes` file must be a plain text file where each line maps an instruction mnemonic to its 7-bit binary opcode, separated by whitespace.

### Example `opcodes.txt`:

```
add	0000000
sub	0000001
mul	0000010
...
jal	1100000
csrr	1110000
```
