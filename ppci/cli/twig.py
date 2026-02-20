import argparse
import sys
from .. import api
from ..lang.c import CAstPrinter, create_ast
from ..lang.c.options import COptions, coptions_parser
from .base import LogSetup, base_parser
from .compile_base import compile_parser, do_compile
from ..arch import get_arch
from ..binutils.linker import link
from ..binutils.layout import (
    Layout,
    Memory,
    Section,
    SymbolDefinition,
    EntrySymbol,
)

parser = argparse.ArgumentParser(
    description="Twig C compiler (alias of 'ppci-cc -m twig')",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[base_parser, compile_parser, coptions_parser],
)
parser.add_argument(
    "-E", action="store_true", default=False, help="Stop after preprocessing"
)
parser.add_argument(
    "-M",
    action="store_true",
    default=False,
    help="Emit makefile dependency rule",
)
parser.add_argument(
    "--ast", action="store_true", default=False, help="Dump C AST and stop"
)
parser.add_argument(
    "-c", action="store_true", default=False, help="Compile only, do not link"
)
parser.add_argument(
    "-ld",
    "--layout",
    help="Custom layout file (overrides default MMIO layout)",
    metavar="LAYOUT",
)
parser.add_argument(
    "--entry", default="main", help="Entry symbol for linking (default: main)"
)
parser.add_argument(
    "--hex-output",
    default="meminit.hex",
    help="Output file for custom 32-bit binary strings",
)
parser.add_argument(
    "sources", metavar="source", nargs="+", type=argparse.FileType("r")
)


def twig(args=None):
    args = parser.parse_args(args)
    with LogSetup(args) as log_setup:
        march = get_arch("twig")
        coptions = COptions()
        coptions.process_args(args)

        if args.E:
            with open(args.output, "w") as out:
                for src in args.sources:
                    api.preprocess(src, out, coptions)
        elif args.M:
            # Dependency generation placeholder
            pass
        elif args.ast:
            with open(args.output, "w") as out:
                printer = CAstPrinter(file=out)
                for src in args.sources:
                    filename = getattr(src, "name", None)
                    ast = create_ast(
                        src, march.info, filename=filename, coptions=coptions
                    )
                    printer.print(ast)
        else:
            # 1. Compile sources to IR
            ir_modules = []
            for src in args.sources:
                ir_module = api.c_to_ir(
                    src, march, coptions=coptions, reporter=log_setup.reporter
                )

                # Optimize (Optional)
                api.optimize(
                    ir_module, level=args.O, reporter=log_setup.reporter
                )

                ir_modules.append(ir_module)

            # --ir, -c, -S
            if args.ir or args.c or args.S:
                do_compile(
                    ir_modules, march, log_setup.reporter, log_setup.args
                )
            else:
                # 2. Compile IR to Object (in-memory)
                march.entry_symbol = args.entry
                obj = api.ir_to_object(
                    ir_modules,
                    march,
                    reporter=log_setup.reporter,
                    debug=args.g,
                )

                # 2b. Append halt (0xFFFFFFFF) after entry function code
                code_section = obj.get_section("code")
                code_section.add_data(b"\xff\xff\xff\xff")

                # 3. Prepare Layout
                if args.layout:
                    with open(args.layout, "r") as f:
                        layout_obj = Layout.load(f)
                else:
                    layout_obj = gen_twig_layout()

                # Can use default layout string
                # layout_obj = Layout.load(io.StringIO(DEFAULT_LAYOUT))

                # 4. Link
                try:
                    linked_obj = link(
                        objects=[obj],
                        layout=layout_obj,
                        entry=args.entry,
                        debug=args.g,
                        reporter=log_setup.reporter,
                    )
                except Exception as e:
                    print(f"Linking error: {e}")
                    sys.exit(1)

                # 5. Output linked object
                output_filename = (
                    args.output if args.output else args.name + ".out"
                )
                with open(output_filename, "w") as f:
                    linked_obj.save(f)

                # 6. Generate custom hex output (meminit.hex)
                if args.hex_output:
                    write_meminit_hex(linked_obj, args.hex_output)


# Default memory layout based on MMIO.md
##############################################
# MMIO  (36B): 0x0000_0000 - 0x0000_0020
# Code  (1MB): 0x0000_0024 - 0x000F_FFFC
# Args (15MB): 0x0010_0000 - 0x00FF_FFFC
# Heap (3.75GB): 0x1000_0000 - 0xF0FF_FFFC
# Stack (250MB): 0xF100_0000 - 0xFFFF_FFFC
##############################################
DEFAULT_LAYOUT = """
MEMORY mmio LOCATION=0x00000000 SIZE=0x00000024 {
    DEFINESYMBOL(mmio_base)
}

MEMORY code_mem LOCATION=0x00000024 SIZE=0xFFFDC {
    SECTION(code)
}

MEMORY args_mem LOCATION=0x00100000 SIZE=0x00F00000 {
    SECTION(data)
    SECTION(rodata)
    SECTION(bss)
}

MEMORY heap_mem LOCATION=0x10000000 SIZE=0xE1000000 {
    DEFINESYMBOL(heap_base)
}

MEMORY stack_mem LOCATION=0xF1000000 SIZE=0x0F000000 {
    DEFINESYMBOL(stack_base)
}
"""


def gen_twig_layout():
    layout = Layout()

    # 1. MMIO region: mapping the hardware registers
    mmio = Memory("mmio")
    mmio.location = 0x00000000
    mmio.size = 0x00000024
    # mmio_base symbol will point to 0x00000000
    mmio.add_input(SymbolDefinition("mmio_base"))
    layout.add_memory(mmio)

    # 2. Code region: starting at 0x24 to bypass the MMIO range
    code_mem = Memory("code_mem")
    code_mem.location = 0x00000024
    code_mem.size = 0x000FFFDC
    code_mem.add_input(Section("code"))
    layout.add_memory(code_mem)

    # 3. Data/Args region: for global variables, constants, and bss
    args_mem = Memory("args_mem")
    args_mem.location = 0x00100000
    args_mem.size = 0x00F00000
    args_mem.add_input(Section("data"))
    args_mem.add_input(Section("rodata"))
    args_mem.add_input(Section("bss"))
    layout.add_memory(args_mem)

    # 4. Heap region: dynamic memory allocation area
    heap_mem = Memory("heap_mem")
    heap_mem.location = 0x10000000
    heap_mem.size = 0xE1000000
    heap_mem.add_input(SymbolDefinition("heap_base"))
    layout.add_memory(heap_mem)

    # 5. Stack region: for function calls and local variables
    stack_mem = Memory("stack_mem")
    stack_mem.location = 0xF1000000
    stack_mem.size = 0x0F000000
    # Note: stack_base points to the start of the memory;
    # actual SP usually starts at the top (0xFFFFFFFC)
    stack_mem.add_input(SymbolDefinition("stack_base"))
    layout.add_memory(stack_mem)

    # 6. Define Entry Point: where execution begins
    layout.entry = EntrySymbol("main")

    return layout


def write_meminit_hex(obj, filename):
    """
    Writes the object code to a file as 32-bit binary strings (0101...).
    """
    # Try to find the 'code_mem' image, fallback to first image if not named
    image = obj.get_image("code_mem")
    if not image and obj.images:
        image = obj.images[0]

    if not image:
        print("Warning: No image found to write hex output.")
        return

    data = image.data
    # Align to 4 bytes
    pad = len(data) % 4
    if pad != 0:
        data += b"\x00" * (4 - pad)

    with open(filename, "w", encoding="utf-8") as f:
        # Process 4 bytes at a time, Little Endian
        for i in range(0, len(data), 4):
            chunk = data[i : i + 4]
            val = int.from_bytes(chunk, byteorder="little", signed=False)
            f.write(f"{val:032b}\n")


if __name__ == "__main__":
    sys.exit(twig())
