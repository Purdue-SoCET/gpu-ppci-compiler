"""TWIG architecture."""

from ... import ir
from ...binutils.assembler import BaseAssembler
from ..arch import Architecture
from ..arch_info import ArchInfo, TypeInfo
from ..data_instructions import DByte, data_isa
from ..generic_instructions import Label, RegisterUseDef
from ..stack import FramePointerLocation, StackLocation
from .asm_printer import TwigAsmPrinter
from .instructions import (
    Add,
    Addi,
    And,
    Cos,
    Csrr,
    Halt,
    Isqrt,
    ItoF,
    FtoI,
    Lli,
    Lmi,
    Lui,
    Lw,
    Mul,
    Prsw,
    Prlw,
    Bl,
    Blr,
    Slli,
    Srli,
    Sw,
    Sin,
    isa,
    Align,
    Section,
    dcd,
)
from .registers import (
    R0,
    LR,
    SP,
    FP,
    R3,
    R4,
    R5,
    R6,
    R7,
    R9,
    R10,
    R11,
    R12,
    R13,
    R14,
    R15,
    R16,
    R17,
    R18,
    R19,
    R20,
    R21,
    R22,
    R23,
    R24,
    R25,
    R26,
    R27,
    R28,
    R29,
    R30,
    R31,
    R32,
    R33,
    R34,
    R35,
    R36,
    R37,
    R38,
    R39,
    R40,
    R41,
    R42,
    R43,
    R44,
    R45,
    R46,
    R47,
    R48,
    R49,
    R50,
    R51,
    R52,
    R53,
    R54,
    R55,
    R56,
    R57,
    R58,
    R59,
    R60,
    R61,
    R62,
    R63,
    Register,
    TwigRegister,
    gdb_registers,
    register_classes_swfp,
)

BUILTIN_TABLE = {
    "sin": Sin,
    "cos": Cos,
    "isqrt": Isqrt,
    "itof": ItoF,
    "ftoi": FtoI,
}

# def isinsrange(bits, val) -> bool:
#     msb = 1 << (bits - 1)
#     ll = -msb
#     return bool(val <= (msb - 1) and (val >= ll))

NUM_THREADS = 32
# Fixed space for saving predicate registers during function calls.
# 32 pred regs * 4 bytes each = 128 bytes. Predicates are shared masks
# (not per-thread), so this is NOT multiplied by NUM_THREADS.
PRED_SAVE_SPACE = 128

# Base address for stack in entry function setup:
# SP = BASE_STACK + global_tid * totalstack
BASE_STACK = 0x100000


class TwigAssembler(BaseAssembler):
    def __init__(self):
        super().__init__()
        self.lit_pool = []
        self.lit_counter = 0

    def flush(self):
        if self.in_macro:
            raise Exception()
        while self.lit_pool:
            i = self.lit_pool.pop(0)
            self.emit(i)

    def add_literal(self, v):
        """For use in the pseudo instruction LDR r0, =SOMESYM"""
        # Invent some label for the literal and store it.
        assert type(v) is str
        self.lit_counter += 1
        label_name = f"_lit_{self.lit_counter}"
        self.lit_pool.append(Label(label_name))
        self.lit_pool.append(dcd(v))
        return label_name


class TwigArch(Architecture):
    name = "twig"

    def __init__(self, options=None):
        super().__init__()

        self.isa = isa + data_isa
        self.store = Sw
        self.load = Lw
        self.regclass = register_classes_swfp
        self.fp_location = FramePointerLocation.TOP
        self.fp = FP
        # self.isa.sectinst = Section
        # self.isa.dbinst = DByte
        # self.isa.dsinst = DZero
        self.gdb_registers = gdb_registers
        # self.gdb_pc = PC
        # self.asm_printer = TwigAsmPrinter()
        if TwigAsmPrinter:
            self.asm_printer = TwigAsmPrinter()
        self.assembler = TwigAssembler()
        self.assembler.gen_asm_parser(self.isa)

        self.info = ArchInfo(
            type_infos={
                ir.i8: TypeInfo(1, 1),
                ir.u8: TypeInfo(1, 1),
                ir.i16: TypeInfo(2, 2),
                ir.u16: TypeInfo(2, 2),
                ir.i32: TypeInfo(4, 4),
                ir.u32: TypeInfo(4, 4),
                ir.f32: TypeInfo(4, 4),
                "int": ir.i32,
                "long": ir.i32,
                "ptr": ir.u32,
                "float": ir.f32,
                "double": ir.f32,
                ir.ptr: ir.u32,
            },
            register_classes=self.regclass,
            simt_threads=NUM_THREADS,
        )

        self._arg_regs = [R12, R13, R14, R15, R16, R17]
        self._ret_reg = R10
        # all should be callee saved? - besides predicate
        self.callee_save = (
            R9,
            R18,
            R19,
            R20,
            R21,
            R22,
            R23,
            R24,
            R25,
            R26,
            R27,
        )
        self.caller_save = (
            R10,
            R11,
            R12,
            R13,
            R14,
            R15,
            R16,
            R17,
            R28,
            R29,
            R30,
            R31,
            R32,
            R33,
            R34,
            R35,
            R36,
            R37,
            R38,
            R39,
            R40,
            R41,
            R42,
            R43,
            R44,
            R45,
            R46,
            R47,
            R48,
            R49,
            R50,
            R51,
            R52,
            R53,
            R54,
            R55,
            R56,
            R57,
            R58,
            R59,
            R60,
            R61,
            R62,
        )  # + tuple(predregisters)

    def branch(self, reg, lab):
        if isinstance(lab, TwigRegister):
            return Blr(reg, lab, 0, clobbers=self.caller_save)
        else:
            return Bl(reg, lab, clobbers=self.caller_save)

    # def get_runtime(self):
    #     """Implement compiler runtime functions"""
    #     from ...api import asm

    #     asm_src = """
    #     __sdiv:
    #     ; Divide x12 by x13
    #     ; x14 is a work register.
    #     ; x10 is the quotient

    #     mv x10, x0     ; Initialize the result
    #     li x14, 1      ; mov divisor into temporary register.

    #     ; Blow up part: blow up divisor until it is larger than the divident.
    #     __shiftl:
    #     bge x13, x12, __cont1
    #     slli x13, x13, 1
    #     slli x14, x14, 1
    #     j __shiftl

    #     ; Repeatedly substract shifted versions of divisor
    #     __cont1:
    #     beq x14, x0, __exit
    #     blt x12, x13, __skip
    #     sub x12, x12, x13
    #     or x10, x10, x14
    #     __skip:
    #     srli x13, x13, 1
    #     srli x14, x14, 1
    #     j __cont1

    #     __exit:
    #     jalr x0,ra,0
    #     """
    #     return asm(io.StringIO(asm_src), self)

    def immUsed(self, r1, r2, offset, instruction, pred=0):
        if offset in range(-32, 32):
            if instruction == "addi":
                yield Addi(r1, r2, offset, pred)
            if instruction == "lw":
                yield Lw(r1, offset, r2, pred)
            if instruction == "sw":
                yield Sw(r1, offset, r2, pred)
        else:
            upper_8 = (offset >> 24) & 0xFF
            middle_12 = (offset >> 12) & 0xFFF
            lower_12 = (offset) & 0xFFF
            yield Lui(R63, upper_8, pred)
            yield Lmi(R63, middle_12, pred)
            yield Lli(R63, lower_12, pred)

            if instruction == "addi":
                yield Add(r1, r2, R63, pred)
            if instruction == "lw":
                # r2 is the address; add offset for new address
                yield Add(R63, r2, R63, pred)
                yield Lw(r1, 0, R63, pred)
            if instruction == "sw":
                yield Add(R63, r2, R63, pred)
                yield Sw(r1, 0, R63, pred)
        return

    def gen_twig_memcpy(self, dst, src, tmp, size, pred=0):
        # Called before register allocation
        for i in range(0, size, 4):
            yield from self.immUsed(tmp, src, i, "lw", pred=pred)
            yield from self.immUsed(tmp, dst, i, "sw", pred=pred)

    def peephole(self, frame):
        """
        Fixes up frame-pointer-relative (fprel) offsets to account for the
        LR/FP save area and callee-saved registers that sit between SP and the
        variables. ins.offset is the raw negative offset assigned by the
        allocator (TOP frame pointer); the final offset from FP is:
          final_offset = callee_save_space + round_up(stacksize) + ins.offset
        """
        new_instructions = []
        saved_registers = self.get_callee_saved(frame)
        callee_save_space = 4 * len(saved_registers)
        scalar_stack_size = round_up(frame.stacksize)
        for ins in frame.instructions:
            if hasattr(ins, "fprel") and ins.fprel:
                final_offset = callee_save_space + scalar_stack_size + ins.offset
                curr_pred = getattr(ins, "pred", 0)
                if isinstance(ins, Lw):
                    new_instructions.extend(
                        self.immUsed(
                            ins.rd, ins.rs1, final_offset, "lw", curr_pred
                        )
                    )
                elif isinstance(ins, Sw):
                    new_instructions.extend(
                        self.immUsed(
                            ins.rs2, ins.rs1, final_offset, "sw", curr_pred
                        )
                    )
                elif isinstance(ins, Addi):
                    new_instructions.extend(
                        self.immUsed(
                            ins.rd, ins.rs1, final_offset, "addi", curr_pred
                        )
                    )
                else:
                    raise TypeError(f"Unhandled fprel instruction: {ins}")
            else:
                new_instructions.append(ins)
        return new_instructions

    def move(self, dst, src):
        """Generate a move from src to dst"""
        return Addi(dst, src, 0, 0, ismove=True)

    def gen_entry_stack_setup(self, frame, pred=0):
        """Emit instructions to set SP for all threads at entry.
        Each thread gets its own private stack frame:
          global_tid = Bid * BlkDim + tid
          SP = BASE_STACK + global_tid * totalstack

        tid = csrr(0), Bid = csrr(1), BlkDim = csrr(2)

        Uses only R3-R7, R9, R11 as temporaries so that R12-R17 (argument
        registers per ABI) and R10 (return value) are preserved for the kernel.
        """
        stack_size = round_up(frame.stacksize)
        calleeregs = self.get_callee_saved(frame)
        savespace = 4 * len(calleeregs)
        extras = max(frame.out_calls) if frame.out_calls else 0
        outspace = round_up(extras)
        lrfpspace = 8
        predsavespace = PRED_SAVE_SPACE
        totalstack = round_up(
            stack_size + savespace + outspace + lrfpspace + predsavespace
        )
        self._entry_totalstack = totalstack
        # R9=tid, R11=Bid, R3=BlkDim (avoid R10, R12-R17)
        yield Csrr(R9, 0, pred)
        yield Csrr(R11, 1, pred)
        yield Csrr(R3, 2, pred)
        # R5 = Bid * BlkDim
        yield Mul(R5, R11, R3, pred)
        # R7 = global_tid = Bid * BlkDim + tid
        yield Add(R7, R5, R9, pred)
        # R4 = totalstack constant
        if totalstack in range(-32, 32):
            yield Addi(R4, R0, totalstack, pred)
        else:
            upper_8 = (totalstack >> 24) & 0xFF
            middle_12 = (totalstack >> 12) & 0xFFF
            lower_12 = totalstack & 0xFFF
            yield Addi(R4, R0, 0, pred)
            if upper_8 != 0:
                yield Lui(R4, upper_8, pred)
            if middle_12 != 0:
                yield Lmi(R4, middle_12, pred)
            if lower_12 != 0:
                yield Lli(R4, lower_12, pred)
        # R5 = global_tid * totalstack
        yield Mul(R5, R7, R4, pred)
        # R6 = BASE_STACK
        yield from self.immUsed(R6, R0, BASE_STACK, "addi", pred)
        # SP = BASE_STACK + global_tid * totalstack
        yield Add(SP, R6, R5, pred)
        for r in [R9, R11, R3, R4, R5, R6, R7]:
            yield Addi(r, R0, 0, pred)

    def gen_prologue(self, frame):
        """Adjust sp, save lr and fp, save callee saves on stack,
        and reserve space for predicate saves during calls."""
        yield Label(frame.name)
        entry_symbol = getattr(self, "entry_symbol", None)
        if entry_symbol is not None and frame.name == entry_symbol:
            yield from self.gen_entry_stack_setup(frame)
        stack_size = round_up(frame.stacksize)
        lrfpspace = 8
        calleeregs = self.get_callee_saved(frame)
        savespace = 4 * len(calleeregs)
        extras = max(frame.out_calls) if frame.out_calls else 0
        outspace = round_up(extras)
        predsavespace = PRED_SAVE_SPACE
        totalstack = round_up(
            stack_size + savespace + outspace + lrfpspace + predsavespace
        )
        if totalstack > 0:
            yield from self.immUsed(SP, SP, -totalstack, "addi")

        yield from self.immUsed(LR, SP, 4, "sw")
        yield from self.immUsed(FP, SP, 0, "sw")

        yield from self.immUsed(FP, SP, 8, "addi")

        if savespace > 0:
            offset = 0
            for register in calleeregs:
                yield from self.immUsed(register, FP, offset, "sw")
                offset += 4
        return

    def gen_epilogue(self, frame):
        """restore callee-saves, reload LR and FP, deallocate stack"""
        stack_size = round_up(frame.stacksize)
        calleeregs = self.get_callee_saved(frame)
        savespace = 4 * len(calleeregs)
        extras = max(frame.out_calls) if frame.out_calls else 0
        outspace = round_up(extras)
        lrfpspace = 8
        predsavespace = PRED_SAVE_SPACE
        totalstack = round_up(
            stack_size + savespace + outspace + lrfpspace + predsavespace
        )

        if savespace > 0:
            offset = 0
            for register in calleeregs:
                yield from self.immUsed(register, FP, offset, "lw")
                offset += 4

        entry_symbol = getattr(self, "entry_symbol", None)
        is_entry = entry_symbol is not None and frame.name == entry_symbol

        yield from self.immUsed(LR, SP, 4, "lw")
        yield from self.immUsed(FP, SP, 0, "lw")
        if totalstack > 0:
            yield from self.immUsed(SP, SP, totalstack, "addi")

        if is_entry:
            yield Halt()
        else:
            yield Blr(R0, LR, 0)
        # yield from self.litpool(frame)
        yield Align(4)
        return

    def _get_pred_save_offset(self, frame):
        """Compute the byte offset from FP to the predicate save area.

        Stack layout from FP upward:
            FP+0:  callee-saved GPRs (savespace)
            FP+savespace: local variables (stack_size)
            FP+savespace+stack_size: outgoing call area (outspace)
            FP+savespace+stack_size+outspace: predicate save area (128 bytes)
        """
        calleeregs = self.get_callee_saved(frame)
        savespace = 4 * len(calleeregs)
        stack_size = round_up(frame.stacksize)
        extras = max(frame.out_calls) if frame.out_calls else 0
        outspace = round_up(extras)
        return savespace + stack_size + outspace

    def gen_call(self, frame, label, args, rv, pred=0):
        """Implement actual call and save / restore live registers.
        For standard calls, saves active predicate registers (P0..P[pred])
        before the call and restores them afterward. The callee's root
        predicate P0 is initialized from the caller's active predicate."""
        name = str(getattr(label, "name", label))
        impl = BUILTIN_TABLE.get(name)
        if impl is not None:
            if not args or rv is None:
                return  # raise or log here if want stricter behavior
            src = args[0][1]
            dst = rv[1]
            yield impl(dst, src, pred)
            return
        if label == "threadIdx":
            ret_vreg = rv[1]
            yield Csrr(ret_vreg, 0, pred)
            return
        if label == "blockIdx":
            ret_vreg = rv[1]
            yield Csrr(ret_vreg, 1, pred)
            return
        if label == "blockDim":
            ret_vreg = rv[1]
            yield Csrr(ret_vreg, 2, pred)
            return
        if label == "argPtr":
            ret_vreg = rv[1]
            yield Csrr(ret_vreg, 3, pred)
            return
        # --- If not custom calls, proceed with a standard function call ---
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)
        stack_size = 0
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, TwigRegister):
                yield self.move(arg_loc, arg)
            elif isinstance(arg_loc, StackLocation):
                stack_size += arg_loc.size
                if isinstance(arg, TwigRegister):
                    yield from self.immUsed(
                        arg, SP, arg_loc.offset, "sw"
                    )
                elif isinstance(arg, StackLocation):
                    p1 = frame.new_reg(TwigRegister)
                    p2 = frame.new_reg(TwigRegister)
                    v3 = frame.new_reg(TwigRegister)

                    # Destination location:
                    yield from self.immUsed(
                        p1, SP, arg_loc.offset, "addi"
                    )
                    saved_registers = self.get_callee_saved(frame)
                    callee_save_space = 4 * len(saved_registers)
                    scalar_stack_size = round_up(frame.stacksize)
                    final_fp_offset = callee_save_space + scalar_stack_size + arg.offset
                    yield from self.immUsed(
                        p2, self.fp, final_fp_offset, "addi"
                    )
                    yield from self.gen_twig_memcpy(p1, p2, v3, arg.size)
                else:  # pragma: no cover
                    raise NotImplementedError("Parameters in memory not impl")

        frame.add_out_call(stack_size)

        arg_regs = {
            arg_loc for arg_loc in arg_locs if isinstance(arg_loc, Register)
        }
        yield RegisterUseDef(uses=arg_regs)

        # --- Save active predicates before call ---
        # Save P0..P[pred] to the predicate save area on the stack.
        # Compute base address of pred save area in R63.
        pred_save_offset = self._get_pred_save_offset(frame)
        yield from self.immUsed(R63, FP, pred_save_offset, "addi")
        for i in range(pred + 1):
            yield Prsw(i, R63, i * 4)
        # Initialize callee's P0 from caller's active predicate
        if pred != 0:
            yield Prlw(0, R63, pred * 4)  # P0 = saved P[pred]

        yield self.branch(LR, label)

        # --- Restore predicates after call returns ---
        yield from self.immUsed(R63, FP, pred_save_offset, "addi")
        for i in range(pred + 1):
            yield Prlw(i, R63, i * 4)

        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield RegisterUseDef(defs=(retval_loc,))
            yield self.move(rv[1], retval_loc)

    def gen_function_enter(self, args):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = {
            arg_loc for arg_loc in arg_locs if isinstance(arg_loc, Register)
        }
        yield RegisterUseDef(defs=arg_regs)

        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, Register):
                yield self.move(arg, arg_loc)
            elif isinstance(arg_loc, StackLocation):
                if isinstance(arg, TwigRegister):
                    yield from self.immUsed(R63, FP, -8, "lw")
                    yield from self.immUsed(
                        arg, R63, arg_loc.offset, "lw"
                    )
                else:
                    pass
            else:  # pragma: no cover
                raise NotImplementedError("Parameters in memory not impl")

    def gen_function_exit(self, rv):
        live_out = set()
        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield self.move(retval_loc, rv[1])
            live_out.add(retval_loc)
        yield RegisterUseDef(uses=live_out)

    def determine_arg_locations(self, arg_types):
        """
        Given a set of argument types, determine location for argument
        ABI:
        pass args in R12-R17
        return values in R10
        """
        locations = []
        regs = [R12, R13, R14, R15, R16, R17]

        offset = 0
        for a in arg_types:
            if a.is_blob:
                r = StackLocation(offset, a.size)
                offset += a.size
            else:
                if regs:
                    r = regs.pop(0)
                else:
                    arg_size = self.info.get_size(a)
                    r = StackLocation(offset, arg_size)
                    offset += arg_size
            locations.append(r)
        return locations

    def determine_rv_location(self, ret_type):
        # return x10
        return self._ret_reg

    def litpool(self, frame):
        """Generate instruction for the current literals"""
        yield Section("data")
        # Align at 4 byte
        if frame.constants:
            yield Align(4)

        # Add constant literals:
        while frame.constants:
            label, value = frame.constants.pop(0)
            yield Label(label)
            if isinstance(value, (int, str)):
                yield dcd(value)
            elif isinstance(value, bytes):
                for byte in value:
                    yield DByte(byte)
                yield Align(4)  # Align at 4 bytes
            else:  # pragma: no cover
                raise NotImplementedError(f"Constant of type {value}")

        yield Section("code")

    def between_blocks(self, frame):
        return []
        # yield from self.litpool(frame)

    def get_callee_saved(self, frame):
        saved_registers = []
        for register in self.callee_save:
            if frame.is_used(register, self.info.alias):
                saved_registers.append(register)
        return saved_registers


def round_up(s):
    return s + (16 - s % 16)
