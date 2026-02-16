import sys
from ppci.api import c_to_ir, ir_to_assembly, get_arch, link, cc
from ppci.ir import Module
from ppci.binutils.objectfile import print_object


def main():
    if len(sys.argv) != 2:
        print("Usage: python compile_twig.py <c_file>")
        print(
            "Compiles the C file to .ir (IR) and .s (assembly) using Twig backend"
        )
        sys.exit(1)

    c_file = sys.argv[1]
    if not c_file.endswith(".c"):
        print("Error: File must have .c extension")
        sys.exit(1)

    try:
        with open(c_file, "r") as f:
            march = get_arch("twig")
            print("Generating IR...")
            ir_module = c_to_ir(f, march)
            print(f"IR:\n{ir_module}")
            print("IR generated successfully")

        # Output IR
        ir_filename = c_file.replace(".c", ".ir")
        with open(ir_filename, "w") as ir_f:
            print(ir_module, file=ir_f)
        print(f"IR output written to {ir_filename}")

        # Output assembly
        print("Generating assembly...")
        asm_code = ir_to_assembly([ir_module], march)
        print("Assembly generated successfully")
        asm_filename = c_file.replace(".c", ".s")
        with open(asm_filename, "w") as asm_f:
            asm_f.write(asm_code)
        print(f"Assembly output written to {asm_filename}")

    except Exception as e:
        import traceback

        print(f"Error during compilation: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
