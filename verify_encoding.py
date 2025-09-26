#!/usr/bin/env python3

from ppci.api import cc
import io

def main():
    # Read and compile the test program
    with open('test_cos.c', 'r') as f:
        source = f.read()

    obj = cc(io.StringIO(source), 'riscv')

    # Get the code section binary data
    code_section = obj.get_section('code')
    code_data = code_section.data

    # Write hex dump to test.hex file
    with open('test.hex', 'w') as f:
        f.write("Hex dump of instructions (4 bytes per instruction):\n")

        # Print hex encoding of each 4-byte instruction
        for i in range(0, len(code_data), 4):
            if i + 4 <= len(code_data):
                # RISC-V is little-endian, so reverse bytes for display
                instruction_bytes = code_data[i:i+4]
                hex_value = instruction_bytes[::-1].hex()  # Convert to big-endian hex
                f.write(f"0x{i:04x}: 0x{hex_value}\n")

        f.write("\nExpected custom instruction encodings:\n")
        f.write("Customcos (customcos x10, x12, x13): 0xe0d60501\n")
        f.write("Customsin (customsin x10, x12, x13): 0x00d67500\n")

        # Look for our custom instructions in the binary
        found_cos = False
        found_sin = False

        for i in range(0, len(code_data), 4):
            if i + 4 <= len(code_data):
                # Get the bytes as stored (little-endian)
                word_le = code_data[i:i+4]
                # Convert to hex for display (big-endian)
                hex_be = word_le[::-1].hex()

                # Check for custom instructions (compare big-endian hex)
                if hex_be == 'e0d60501':
                    f.write(f"[FOUND] Customcos instruction at address 0x{i:04x}\n")
                    found_cos = True
                elif hex_be == '00d67500':
                    f.write(f"[FOUND] Customsin instruction at address 0x{i:04x}\n")
                    found_sin = True

        if found_cos and found_sin:
            f.write("\nSUCCESS: Both custom instructions found with correct encodings!\n")
        else:
            f.write(f"\nISSUE: Customcos found: {found_cos}, Customsin found: {found_sin}\n")

        # Also show the assembly for reference
        f.write("\nFor reference, here's the assembly output:\n")
        from ppci.api import c_to_ir, ir_to_assembly
        ir = c_to_ir(io.StringIO(source), 'riscv')
        asm = ir_to_assembly([ir], 'riscv')
        # Just show the relevant lines
        lines = asm.split('\n')
        for line in lines:
            if 'custom' in line:
                f.write(f"  {line.strip()}\n")

    print("Output written to test.hex")

if __name__ == '__main__':
    main()
