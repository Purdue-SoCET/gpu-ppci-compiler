Download all files under test_merge branch in compiler repo.
https://github.com/Purdue-SoCET/gpu-ppci-compiler/tree/test_merge

`make dev-install` to install package and commands.

# Twig
We use commands to compile files. For example, `twig -S test.c` can give you a assembly output in f.out.

Replace -S with other flags below can generate different files for debugging:
- `-E`: Stop after preprocessing
- `--ir`: Intermediate Representation (IR)
- `--ast`: Abstract Syntax Tree (AST)
- `-S`: Assembly file
##### Linker
- `-c`: Linker output, including binary machine code, symbol tables, and jump information.
- `--layout` or `-ld`: layout setting, default `.layout`
- `-o`: Output file
- `--hex-output`: Output hex file, default `meminit.hex`
- `-entry`: Entry function, default `main`
- default: `twig file` will output compiled results in `f.out` and generate `meminit.hex` with binary code.
> `twig src/a.c src/test.c` is same as `twig src/a.c src/test.c -o f.out --hex-output meminit.hex` 

## Layout
- MMIO  (36B): 0x0000_0000 - 0x0000_0020
- Code  (1MB): 0x0000_0024 - 0x000F_FFFC
- Args (15MB): 0x0010_0000 - 0x00FF_FFFC
- Heap (3.75GB): 0x1000_0000 - 0xF0FF_FFFC
- Stack (250MB): 0xF100_0000 - 0xFFFF_FFFC

## Tool
helpful tool command, generate corresponding file.
`tool`
- --asm: assembly -> binary
- --disasm: binary -> assembly
- --bin: 0101 text to raw binary
- --hex: 0101 text to hex
- -o: output file