"""TWIG architecture."""

import io

from ... import ir
from ...binutils.assembler import BaseAssembler
from ..arch import Architecture
from ..arch_info import ArchInfo, TypeInfo
from ..data_instructions import DByte, DZero, data_isa
from ..generic_instructions import Label, RegisterUseDef
from ..stack import FramePointerLocation, StackLocation
from . import instructions
# from .asm_printer import TwigAsmPrinter
from .instructions import (
    #rtype
    Add,
    Sub,
    Mul,
    Div,
    And,
    Or,
    Xor,
    Slt,
    Sltu,
    Addf,
    Subf,
    Mulf,
    Divf,
    Sll,
    Srl,
    Sra,
    #itype
    Addi,
    Subi,
    Ori,
    Slti,
    Sltiu,
    Srli,
    Srai,
    #memory
    Lw,
    Lh,
    Lb,
    Sw,
    Sh,
    Sb,
    #branch
    Beq,
    Bne,
    Bge,
    Bgeu,
    Blt,
    Bltu,
    #jump
    Bl,
    Blr,
    #htype,
    Halt,
    #isa
    isa,
)
from .registers import (
    R0,
    LR,
    SP,
    R3,
    R4,
    R5,
    R6,
    R7,
    FP,
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
    PC,
    P0,
    P1,
    P2,
    P3,
    P4,
    P5,
    P6,
    P7,
    P8,
    P9,
    P10,
    P11,
    P12,
    P13,
    P14,
    P15,
    P16,
    P17,
    P18,
    P19,
    P20,
    P21,
    P22,
    P23,
    P24,
    P25,
    P26,
    P27,
    P28,
    P29,
    P30,
    P31,
    Register,
    TwigRegister,
    TwigPredRegister,
    gdb_registers,
    predregisters,
    # register_classes_hwfp,
    register_classes_swfp,
)

# def isinsrange(bits, val) -> bool:
#     msb = 1 << (bits - 1)
#     ll = -msb
#     return bool(val <= (msb - 1) and (val >= ll))


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

    # def add_literal(self, v):
    #     """For use in the pseudo instruction LDR r0, =SOMESYM"""
    #     # Invent some label for the literal and store it.
    #     assert type(v) is str
    #     self.lit_counter += 1
    #     label_name = f"_lit_{self.lit_counter}"
    #     self.lit_pool.append(Label(label_name))
    #     self.lit_pool.append(dcd(v))
    #     return label_name


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
        # self.asm_printer = TwigAsmPrinter() #TODO work.
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
                # ir.f32: TypeInfo(4, 4), #TODO: 32bit ADD FLOATING SUPPORT
                # ir.f64: TypeInfo(4, 4),
                "int": ir.i32,
                "long": ir.i32,
                "ptr": ir.u32,
                ir.ptr: ir.u32,
            },
            register_classes=self.regclass,
        )

        self._arg_regs = [R12, R13, R14, R15, R16, R17]
        self._ret_reg = R10
        #all should be callee saved? - besides predicate
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
        self.caller_save = (R10, R11, R12, R13, R14, R15, R16, R17) #+ tuple(predregisters)

    # def branch(self, reg, lab):
    #     if isinstance(lab, TwigRegister):
    #         return Blr(reg, lab, 0, clobbers=self.caller_save)
    #     else:
    #         return Bl(reg, lab, clobbers=self.caller_save)

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

    # do we need memcpy ? this might work might not
    # def gen_Twig_memcpy(self, dst, src, tmp, size):
    #     # Called before register allocation
    #     # Major crappy memcpy, can be improved!
    #     for idx in range(size):
    #         yield Lb(tmp, idx, src)
    #         yield Sb(tmp, idx, dst)

    # def peephole(self, frame):
    #     newinstructions = []
    #     for ins in frame.instructions:
    #         if hasattr(ins, "fprel") and ins.fprel:
    #             ins.offset += round_up(frame.stacksize + 8) - 8
    #         newinstructions.append(ins)
    #     return newinstructions

    def move(self, dst, src):
        """Generate a move from src to dst"""
        #rd = rs1 + 0 i think
        return Addi(dst, src, ismove=True)

    def gen_prologue(self, frame):
        """TODO idk, adjust sp, save lr and lp(?), save callee saves on stack"""
        yield Label(frame.name)

    def gen_epilogue(self, frame):
        """restore callee-saves, reload LR and FP, deallocate stack"""
        return
        yield

    def gen_call(self, frame, label, args, rv):
        """Implement actual call and save / restore live registers"""

        # arg_types = [a[0] for a in args]
        # arg_locs = self.determine_arg_locations(arg_types)
        # stack_size = 0
        # # Setup parameters:
        # for arg_loc, arg2 in zip(arg_locs, args):
        #     arg = arg2[1]
        #     if isinstance(arg_loc, (TwigRegister)):
        #         yield self.move(arg_loc, arg)
        #     elif isinstance(arg_loc, StackLocation):
        #         stack_size += arg_loc.size
        #         if isinstance(arg, TwigRegister):
        #             yield Sw(arg, arg_loc.offset, SP)
        #         elif isinstance(arg, StackLocation):
        #             p1 = frame.new_reg(TwigRegister)
        #             p2 = frame.new_reg(TwigRegister)
        #             v3 = frame.new_reg(TwigRegister)

        #             # Destination location:
        #             # Remember that the LR and FP are pushed in between
        #             # So hence -8:
        #             yield instructions.Addi(p1, SP, arg_loc.offset)
        #             # Source location:
        #             yield instructions.Addi(
        #                 p2,
        #                 self.fp,
        #                 arg.offset + round_up(frame.stacksize + 8) - 8,
        #             )
        #             yield from self.gen_Twig_memcpy(p1, p2, v3, arg.size)
        #     else:  # pragma: no cover
        #         raise NotImplementedError("Parameters in memory not impl")

        # # Record that certain amount of stack is required:
        # frame.add_out_call(stack_size)

        # arg_regs = {
        #     arg_loc for arg_loc in arg_locs if isinstance(arg_loc, Register)
        # }
        # yield RegisterUseDef(uses=arg_regs)

        # yield self.branch(LR, label)

        # if rv:
        #     retval_loc = self.determine_rv_location(rv[0])
        #     yield RegisterUseDef(defs=(retval_loc,))
        #     yield self.move(rv[1], retval_loc)
        raise NotImplementedError("Twig gen_call not implemented yet")

    def gen_function_enter(self, args):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        # arg_regs = {
        #     arg_loc for arg_loc in arg_locs if isinstance(arg_loc, Register)
        # }
        # yield RegisterUseDef(defs=arg_regs)

        phys_defs = {loc for loc in arg_locs if isinstance(loc, Register)}
        if phys_defs:
            yield RegisterUseDef(defs=phys_defs)

        #alt for vreg? we don't have virtual memory
        for loc, (_,vreg) in zip(arg_locs, args):
            if isinstance(loc, Register):
                yield self.move(vreg, loc)
            elif isinstance(loc, StackLocation):
                raise NotImplementedError("stack arguments not supported yet")
                if isinstance(arg, TwigRegister):
                    Code = Lw(arg, arg_loc.offset, FP)
                    Code.fprel = True
                    yield Code
                else:
                    pass
            else:  # pragma: no cover
                raise NotImplementedError(f"Unsupported arg location: {type(loc)}")

    def gen_function_exit(self, rv):
        # live_out = set()
        if not rv:
            return
        rv_type, rv_vreg = rv
        ret_reg = self.determine_rv_location(rv_type)
        yield self.move(ret_reg, rv_vreg)
        # Mark it as a live-out so the RA keeps it fixed in the return register.
        yield RegisterUseDef(uses={ret_reg})

    def determine_arg_locations(self, arg_types):
        """
        Given a set of argument types, determine location for argument
        ABI:
        pass args in R12-R17
        return values in R10
        """
        locations = []
        regs = list(self._arg_regs)

        offset = 0
        for a in arg_types:
            if getattr(a, "is_blob", False):
                raise NotImplementedError("Blob/aggregate argument not supported")
            if regs:
                locations.append(regs.pop(0))
            else:
                size = self.info.get_size(a)
                locations.append(StackLocation(offset, size))
                offset += size
        return locations

    def determine_rv_location(self, ret_type):
        #return x10
        return self._ret_reg

    # def gen_prologue(self, frame):
    #     """Returns prologue instruction sequence"""
    #     # Label indication function:
    #     yield Label(frame.name)
    #     ssize = round_up(frame.stacksize + 8)
    #     yield Addi(SP, SP, -ssize)  # Reserve stack space

    #     yield Sw(LR, 4, SP)
    #     yield Sw(FP, 0, SP)


    #     yield Addi(FP, SP, 8)  # Setup frame pointer
    #     # yield Addi(FP, SP, 8)  # Setup frame pointer

    #     saved_registers = self.get_callee_saved(frame)
    #     rsize = 4 * len(saved_registers)
    #     rsize = round_up(rsize)

    #     yield Addi(SP, SP, -rsize)  # Reserve stack space

    #     i = 0
    #     for register in saved_registers:
    #         i -= 4
    #         yield Sw(register, i + rsize, SP)

    #     # Allocate space for outgoing calls:
    #     extras = max(frame.out_calls) if frame.out_calls else 0
    #     if extras:
    #         ssize = round_up(extras)
    #         yield Addi(SP, SP, -ssize)  # Reserve stack space

    # def litpool(self, frame):
    #     """Generate instruction for the current literals"""
    #     yield Section("data")
    #     # Align at 4 byte
    #     if frame.constants:
    #         yield Align(4)

    #     # Add constant literals:
    #     while frame.constants:
    #         label, value = frame.constants.pop(0)
    #         yield Label(label)
    #         if isinstance(value, (int, str)):
    #             yield dcd(value)
    #         elif isinstance(value, bytes):
    #             for byte in value:
    #                 yield DByte(byte)
    #             yield Align(4)  # Align at 4 bytes
    #         else:  # pragma: no cover
    #             raise NotImplementedError(f"Constant of type {value}")

    #     yield Section("code")

    def between_blocks(self, frame):
        return []
        # yield from self.litpool(frame)

    # def gen_epilogue(self, frame):
    #     """Return epilogue sequence for a frame. Adjust frame pointer
    #     and add constant pool
    #     """
    #     # Free space for outgoing calls:
    #     extras = max(frame.out_calls) if frame.out_calls else 0
    #     if extras:
    #         ssize = round_up(extras)
    #         yield Addi(SP, SP, ssize)  # Reserve stack space

    #     # Callee saved registers:
    #     saved_registers = self.get_callee_saved(frame)
    #     rsize = 4 * len(saved_registers)
    #     rsize = round_up(rsize)

    #     i = 0
    #     for register in saved_registers:
    #         i -= 4
    #         yield Lw(register, i + rsize, SP)

    #     yield Addi(SP, SP, rsize)  # Reserve stack space

    #     yield Lw(LR, 4, SP)
    #     yield Lw(FP, 0, SP)

    #     ssize = round_up(frame.stacksize + 8)

    #     yield Addi(SP, SP, ssize)  # Free stack space

    #     # Return

    #     yield Blr(R0, LR, 0)

    #     # Add final literal pool:
    #     yield from self.litpool(frame)
    #     yield Align(4)  # Align at 4 bytes

    # def get_callee_saved(self, frame):
    #     saved_registers = []
    #     for register in self.callee_save:
    #         if frame.is_used(register, self.info.alias):
    #             saved_registers.append(register)
    #     return saved_registers


# def round_up(s):
#     return s + (16 - s % 16)
