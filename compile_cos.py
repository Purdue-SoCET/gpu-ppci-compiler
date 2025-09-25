#!/usr/bin/env python3

from ppci.api import c_to_ir
from ppci.lang.c import COptions
import io

# Read the C source
with open('test_cos.c', 'r') as f:
    source = f.read()

# Compile to IR
coptions = COptions()
ir_module = c_to_ir(io.StringIO(source), 'riscv', coptions=coptions)

# Print the IR
print("IR Module:")
print(ir_module)
print("\nFunctions:")
for func in ir_module.functions:
    print(f"Function: {func.name}")
    for block in func:
        print(f"  Block: {block.name}")
        for ins in block:
            print(f"    {ins}")

# Compile IR to assembly
from ppci.api import ir_to_assembly
asm_code = ir_to_assembly([ir_module], 'riscv')
print("\nAssembly Code:")
print(asm_code)
