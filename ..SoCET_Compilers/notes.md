# TASKS
- Test our parsing multiple files
- Locate where C libary and language are at

# NOTES (Week 11)
## 11/01/25
- ir_diagnosis folder
- ast_diagnosis folder

Types of Compounds:
- Return
- Declarations
- Expressions
- If
- While
- For
- Do-while


ppci\lang\c\codegenerator.py
def gen_if(self, stmt: statements.If)

def gen_while(self, stmt: statements.While)
def gen_do_while(self, stmt: statements.DoWhile)
def gen_for(self, stmt: statements.For)

Things to Consider (will graphics use these and do we need to worry about it)
- Switch
- Case
- Range
- GoTo
- Continue
- Break
- InLine Assembly



## 10/25/25 (Week 10)
- sample1_outputs folder
- sample4_outputs folder
- unit_tests
- notes.md

ppci-cc = PPCI C Compiler
-c (flag) - compile only without linking
*Linking is the final step in the compilation process; take all separte compiled pieces of code (object files) and combine into a runnable executable file
*Object file is the machine code that hardware would run

1) cparser (Frontend)
- Reads higher level code file and parses it into a tree-like structure

2) ccodegen (Middle-end)
- Intermediate Representation (IR); code that is easy to optimize

3) optimize (Optimizer)
- Rearranges IR to make it more efficient

4) codegen (Backend)
- Translates optimized IR into machine code


f.out is a JSON file of the object file that ppci crreated

"arch" - the architecture

"sections"
- "name": "data" - holds global and static variables
- "name": "code" - machine code for the function

"relocations" - note from compiler to linker
- "offset": "0x2c" - at byte 0x2c (44) inside the "code" section, there is an instruction that needs to be fixed
- "symbol_id": 2 - instruction at 0x2c is a branch/jump that is supposed to go to symbol2 (add_epilog)
- "type": "b_imm20" - indicates B-type (branch) instruction with a 20-bit immediate

"symbols" - a human readable name for an address (for jump logic)
- "name": "add" - the function name "add"
  - "binding": "global" - public function
  - "typ": "func" - it's a function
  - "value": "0x0" - address 0x0 is where function is found in code

- "name": "add_block0"
  - "binding": "local" - private symbols
  - "typ": "object"
  - "value": "0x18"
  * compiler's "signpost" for the start of the function's main logic
  * basic block: sequence of instructions executed from top to bottom with no jumps in and jumps out; through Control Flow Graphs

- "name": "add_epilog"
  - "binding": "local" - private symbols
  - "typ": "object"
  - "value": "0x30"
  * Cleanup code that restores any saved registers, restores stack pointer and executes the ret instruction

Overall, goes from "add" -> "add_block0" -> "add_epilog"

Prologue (Setup)
130101fe = addi sp, sp, -32 // Allocate 32 bytes on stack
23221100 = sw ra, 28(sp) // Store return address on stack
23208100 = sw s0, 24(sp) // Store caller's frame point s0 on stack
13048100 = addi s0, sp, 32 //  set frame pointer s0 to top of new stack
130101ff = addi sp, sp, -16 // Allocation another 16 bytes on stack
23269100 = sw s1, 20(sp) // Store saved register s1 on stack
232ac400 = sw a2, 16(sp) // Store argument register a2 on stack
2328d400 = sw a3, 12(sp) // Store argument regsiter a3 on stack

Body (Work)
03254401 = lw a0, 20(s0) // Load first number from stack into register a0
83240401 = lw s1, 16(s0) // Load second number from stack insto s1
33059500 = add a0, a0, s1 // core logic of a + b

Epilogue (Cleanup)
6f000000 = j 48 // Jump to cleanup code
8324c100 = lw s1, 20(sp) // load saved register s1 from stack
13010101 = addi sp, sp 16 // Deallocate 16 bytes on stack
83204100 = lw ra, 28 (sp) // restore return address
03240100 = lw s0, 24 (sp) //restore caller frame point
13010102 = addi sp, sp, 32 // deallocate 32 bytes of stack
67800000 = ret // return to caller function

sp - stack pointer: points to top of stack
fp - frame pointer; points to base of current function's stack frame
ra - return address; return to caller
aX - argument registers
sX - registers this function must save and restore if used
tX - temp registers

The Setup
1) Allocate Stack Space for entire frame
2) Save Caller's Return Address (ra)
3) Save Caller's Frame Pointer (fp)
4) Establish New Frame Point (fp)
5) Save Callee-Saved Registers (sX)

The Work
1) Access Arguments aX and more on stack
2) Use temp registers for calculation
3) Store return value to a0

The Cleanup
1) Restore Callee-Saved Register (sX)
2) Restore Caller's Return Address (ra)
3) Restore Caller's Frame Pointer (fp)
4) Deallocate Stack Frame
5) Return to Caller

Definable Things and Commands
--ast // outputs abstract syntax tree
--ir // generates ir-code
--pycode // generates python code
-O // optimzations

=>
https://github.com/Purdue-SoCET/gpu-ppci-compiler/blob/preprocessing/ppci/cli/cc.py
C Parser File called by ppci-cc

=>
https://github.com/Purdue-SoCET/gpu-ppci-compiler/blob/preprocessing/ppci/api.py
api.c_to_ir; loops through all source files and creates IR

In api.py
def cc() // C compiler; single source file into object file
args: source file; march (architecture); coptions (options for C frontend); debug (debug info)
returns: object file

=>
https://github.com/Purdue-SoCET/gpu-ppci-compiler/blob/preprocessing/ppci/lang/c/api.py
def c_to_ir // C to IR translation
args: source file; march (architecture); coptions (options for C frontend)
returns: "ppci.ir.Module" (the ir_module)



