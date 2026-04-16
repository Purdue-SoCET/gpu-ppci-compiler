Run `make dev-install` to install the package and command-line tools.

# Twig
##### Default
`twig <source.c>` compiles and links the input files, then writes the main output to the default `.out` file.
Extra files are only generated when the corresponding flags are provided.

Examples:
- `twig -S test.c`: Output assembly
- `twig --ir test.c`: Output IR
- `twig --ast test.c`: Output AST
- `twig -E test.c`: Stop after preprocessing
- `twig -c test.c`: Compile only, do not link

##### Flags
- `-E`: Stop after preprocessing
- `--ast`: Dump C Abstract Syntax Tree (AST)
- `--ir`: Dump Intermediate Representation (IR)
- `-S`: Output assembly
- `-c`: Compile only, do not link
- `--output <FILE>` / `-o <FILE>`: Output file, default `f.out`
- `--layout <LAYOUT>` / `-ld <LAYOUT>`: Layout setting, default `.layout`
- `--entry <SYMBOL>`: Entry function, default `main`
- `--no-packetize`: Disable packetization

##### Extra output
- `--bin-output <BIN_OUTPUT>`: Output 32-bit binary strings
- `--hex-output <HEX_OUTPUT>`:Output 32-bit hex strings
- `--stack-info-output <FILE>`: Output stack information in JSON format
- `--packet-histogram <FILE>`: Output packet statistics in SVG format

## Layout
- MMIO  (36B): 0x0000_0000 - 0x0000_0020
- Code  (1MB): 0x0000_0024 - 0x000F_FFFC
- Args (15MB): 0x0010_0000 - 0x00FF_FFFC
- Heap (3.75GB): 0x1000_0000 - 0xF0FF_FFFC
- Stack (250MB): 0xF100_0000 - 0xFFFF_FFFC

## Tool
`tool` command is a helper tool for format conversion and requires an `input_file`.
- `--asm <FILE>`: assembly -> binary
- `--disasm <FILE>`: binary -> assembly
- `--bin`: 0101 text to raw binary
- `--hex`: 0101 text to hex
- `--output <OUTPUT>` / `-o <OUTPUT>`: Output file

## File tree

```text
ppci/
├── arch/
│   ├── arm/
│   ├── avr/
│   ├── jvm/
│   ├── m68k/
│   ├── mcs6500/
│   ├── microblaze/
│   ├── mips/
│   ├── msp430/
│   ├── or1k/
│   ├── riscv/
│   ├── stm8/
│   ├── twig/   -> Backend
│   ├── x86_64/
│   └── xtensa/
├── binutils/
├── build/
├── cil/
├── cli/        -> Command Line
├── codegen/    -> Machine Code
├── cpu/
├── format/
│   ├── dwarf/
│   ├── elf/
│   ├── hunk/
│   └── pefile/
├── graph/
├── irutils/
├── lang/
│   ├── basic/
│   ├── c/      -> Frontend
│   ├── c3/
│   ├── fortran/
│   ├── generic/
│   ├── llvmir/
│   ├── ocaml/
│   ├── pascal/
│   ├── python/
│   └── tools/
├── opt/
├── programs/
├── utils/
└── wasm/
```
