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

## Twig pipeline overview

<table>
  <thead>
    <tr>
      <th width="140">Step</th>
      <th>Files</th>
      <th>Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1. CLI</td>
      <td><code>ppci/cli/twig.py</code></td>
      <td>Parse flags and choose the output path</td>
    </tr>
    <tr>
      <td>2. Frontend</td>
      <td><code>ppci/lang/c/api.py</code>, <code>ppci/lang/c/builder.py</code></td>
      <td>Preprocess, parse, and check C input</td>
    </tr>
    <tr>
      <td>3. IR</td>
      <td><code>ppci/lang/c/codegenerator.py</code>, <code>ppci/api.py</code></td>
      <td>Lower C AST into PPCI IR and hand off to the backend</td>
    </tr>
    <tr>
      <td>4. Lowering</td>
      <td><code>ppci/codegen/codegen.py</code>, <code>ppci/codegen/predicate_alloc.py</code>, <code>ppci/arch/twig/instructions.py</code>, <code>ppci/arch/twig/arch.py</code></td>
      <td>Allocate predicates, select Twig instructions, and apply backend policy</td>
    </tr>
    <tr>
      <td>5. Link</td>
      <td><code>ppci/binutils/linker.py</code></td>
      <td>Link the final image</td>
    </tr>
  </tbody>
</table>

## Output stages and which files handle them

<table>
  <thead>
    <tr>
      <th width="88">Output</th>
      <th width="96">Flag</th>
      <th>Main files</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>AST</td>
      <td><code>--ast</code></td>
      <td><code>ppci/cli/twig.py</code> -&gt; <code>ppci/lang/c/builder.py</code> -&gt; <code>ppci/lang/c/preprocessor.py</code> -&gt; <code>ppci/lang/c/parser.py</code> -&gt; <code>ppci/lang/c/utils.py</code></td>
    </tr>
    <tr>
      <td>IR</td>
      <td><code>--ir</code></td>
      <td><code>ppci/cli/twig.py</code> -&gt; <code>ppci/lang/c/api.py</code> -&gt; <code>ppci/lang/c/builder.py</code> -&gt; <code>ppci/lang/c/codegenerator.py</code> -&gt; <code>ppci/cli/compile_base.py</code> -&gt; <code>ppci/irutils/writer.py</code></td>
    </tr>
    <tr>
      <td>asm</td>
      <td><code>-S</code></td>
      <td><code>ppci/cli/twig.py</code> -&gt; <code>ppci/cli/compile_base.py</code> -&gt; <code>ppci/api.py:ir_to_stream</code> -&gt; <code>ppci/codegen/codegen.py</code> -&gt; <code>ppci/binutils/outstream.py</code> -&gt; <code>ppci/arch/twig/asm_printer.py</code></td>
    </tr>
    <tr>
      <td>link</td>
      <td></td>
      <td><code>ppci/cli/twig.py</code> -&gt; <code>ppci/api.py:optimize</code> -&gt; <code>ppci/api.py:ir_to_object</code> -&gt; <code>ppci/binutils/linker.py</code></td>
    </tr>
  </tbody>
</table>

## Key file tree

```text
ppci/
├── cli/
│   ├── twig.py                  -> Twig CLI entry
│   ├── tool.py                  -> Assembles, disassembles, and converts Twig formats
│   └── compile_base.py          -> Writes IR and asm outputs
├── lang/
│   └── c/
│       ├── api.py               -> C frontend entry points
│       ├── builder.py           -> Preprocesses, parses, and checks C
│       ├── preprocessor.py      -> Expands macros and includes
│       ├── parser.py            -> Builds the C AST
│       ├── utils.py             -> AST printers and helpers
│       ├── printer.py           -> Prints AST back to C-like text
│       └── codegenerator.py     -> Lowers C AST into IR
├── api.py                       -> Bridges IR into backend codegen
├── ir.py                        -> Defines IR nodes like `PJump`
├── codegen/
│   ├── codegen.py               -> Instruction selection and emission
│   ├── predicate_alloc.py       -> Maps virtual to physical predicates
│   ├── irdag.py                 -> Connects IR to selection patterns
│   └── packetize.py             -> Packs Twig instructions
├── arch/
│   └── twig/
│       ├── arch.py              -> Twig backend policy and frame lowering
│       ├── asm_printer.py       -> Prints Twig assembly text
│       ├── instructions.py      -> Twig ISA patterns and lowering
│       ├── registers.py         -> Twig register definitions
│       ├── relocations.py       -> Twig relocation records
│       ├── reporter.py          -> Packet histogram output
│       ├── tokens.py            -> Instruction bitfield layouts
│       └── __init__.py          -> Exports `TwigArch`
├── binutils/
│   ├── linker.py                -> Links the final image
│   ├── layout.py                -> Loads memory layouts
│   ├── outstream.py             -> Emits assembly text streams
│   └── objectfile.py            -> Stores sections and relocations
```
