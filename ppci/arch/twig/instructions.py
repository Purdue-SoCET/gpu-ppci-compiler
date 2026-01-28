from ..isa import Isa
from ..encoding import Instruction, Operand, Syntax
from .tokens import *
from .registers import (
    TwigRegister, TwigPredRegister, R0, FP
)
from .relocations import *
from ..generic_instructions import (
    Alignment,
    ArtificialInstruction,
    Global,
    RegisterUseDef,
    SectionInstruction
)
from ..data_instructions import Dd, Dcd2

import struct

isa = Isa()

isa.register_relocation(JImm17Relocation)

class TwigRInstruction(Instruction):
    tokens = [TwigRToken]
    isa = isa

def make_r(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    pred = Operand("pred", int)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, ",", " ", pred])
    tokens = [TwigRToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
    }
    name = mnemonic.title() + "R"
    return type(name, (TwigRInstruction,), members)

# should change opcode ("inst", opcode) to binary (currently decimal)
#rtype
Add = make_r("add", 0)
Sub = make_r("sub", 1)
Mul = make_r("mul", 2)
Div = make_r("div", 3)
And = make_r("and", 4)
Or = make_r("or", 5)
Xor = make_r("xor", 6)
Slt = make_r("slt", 7)
Sltu = make_r("sltu", 8)
Addf = make_r("addf", 9)
Subf = make_r("subf", 10)
Mulf = make_r("mulf", 11)
Divf = make_r("divf", 12)
Sll = make_r("sll", 13)
Srl = make_r("srl", 14)
Sra = make_r("sra", 15)

#itype

class TwigIInstruction(Instruction):
    tokens = [TwigIToken]
    isa = isa

# class IBase(TwigIInstruction):
#     def encode(self):
#         tokens = self.get_tokens()
#         tokens[0][0:7] = self.opcode
#         tokens[0][7:13] = self.rd.num
#         tokens[0][13:19] = self.rs1.num
#         tokens[0][19:25] = self.imm
#         tokens[0][25:30] = self.pred.num
#         tokens[0][30:31] = self.pstart
#         tokens[0][31:32] = self.pend
#         return tokens[0].encode()

def make_i(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    offset = Operand("offset", int)
    pred = Operand("pred", int)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    tokens = [TwigIToken]
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", offset, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", offset, ",", " ", pred])
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "offset": offset,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "tokens": tokens,
        "patterns": patterns,
        "opcode": opcode
    }
    return type(mnemonic + "_ins", (TwigIInstruction,), members)

Addi = make_i("addi", 0b0010000)
Subi = make_i("subi", 0b0010001)
Xori = make_i("xori", 0b0010100)
Ori = make_i("ori", 0b0010101)
Slti = make_i("slti", 0b0010111)
Sltiu = make_i("sltiu", 0b0011000)
Slli = make_i("slli", 0b0011101)
Srli = make_i("srli", 0b0011110)
Srai = make_i("srai", 0b0011111)

#ftype (custom mapping)

class TwigFInstruction(Instruction):
    tokens = [TwigFToken]
    isa = isa

class Cos(TwigFInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    syntax = Syntax(["cos", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0101010
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()

class Sin(TwigFInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    syntax = Syntax(["sin", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0101001
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()


class Isqrt(TwigFInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    syntax = Syntax(["isqrt", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0101000
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()

class ItoF(TwigFInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    syntax = Syntax(["itof", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0101011
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()

class FtoI(TwigFInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    syntax = Syntax(["ftoi", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0101100
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()

class TwigCRInstruction(Instruction):
    tokens = [TwigCRToken]
    isa = isa

class Csrr(TwigCRInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", int)
    pred = Operand("pred", int)
    syntax = Syntax(["csrr", " ", rd, ",", " ", rs1, ",", " ", pred])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b1011000
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        return tokens[0].encode()

#loads
def make_load(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    offset = Operand("offset", int)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", int)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", offset, "(", rs1, ")", ",", " ", pred])
    tokens = [TwigIToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "tokens": tokens,
        "patterns": patterns,
        "fprel": fprel,
        "offset": offset,
        "rd": rd,
        "rs1": rs1,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "opcode": opcode
    }
    return type(mnemonic.title(), (TwigIInstruction,), members)

Lw = make_load("lw", 0b01000000)
Lh = make_load("lh", 0b01000001)
Lb = make_load("lb", 0b01000010)

class TwigSInstruction(Instruction):
    tokens = [TwigSToken]
    isa = isa

def make_store(mnemonic, opcode):
    rs1 = Operand("rs1", TwigRegister, read=True)
    offset = Operand("offset", int)
    rs2 = Operand("rs2", TwigRegister, read=True)
    pred = Operand("pred", int)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rs2, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rs2, ",", " ", offset, "(", rs1, ")", ",", " ", pred])
    tokens = [TwigSToken]
    patterns = {
        "opcode": opcode,
        "rs2": rs2,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "tokens": tokens,
        "patterns": patterns,
        "fprel": fprel,
        "offset": offset,
        "rs2": rs2,
        "rs1": rs1,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "opcode": opcode
    }
    return type(mnemonic.title(), (TwigSInstruction,), members)

Sw = make_store("sw", 0b0110000)
Sh = make_store("sh", 0b0110001)
Sb = make_store("sb", 0b0110010)

class TwigJInstruction(Instruction):
    tokens = [TwigJToken]
    isa = isa

# class B(RiscvInstruction):
#     target = Operand("target", str)
#     syntax = Syntax(["j", " ", target])

#     def encode(self):
#         tokens = self.get_tokens()
#         tokens[0][0:7] = 0b1101111
#         tokens[0][7:12] = 0
#         return tokens[0].encode()

#     def relocations(self):
#         return [BImm20Relocation(self.target)]

#jal
class Bl(TwigJInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    target = Operand("target", str)
    syntax = Syntax(["jal", " ", rd, ",", " ", target])
    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b1100000 #jal opcode
        tokens[0][7:13] = self.rd.num
        tokens[0][13:30] = 0
        # tokens[0][30] = 0b0 #start of new packet
        # tokens[0][31] = 0b1 # end of curr packet
        return tokens[0].encode()

    def relocations(self):

        return [JImm17Relocation(self.target)]

class TwigJrInstruction(Instruction):
    tokens = [TwigJrToken]
    isa = isa

#jalr
class Blr(TwigJrInstruction):
    target = Operand("target", str)
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    offset = Operand("offset", int)
    syntax = Syntax(["jalr", " ", rd, ",", rs1, ",", " ", offset])

    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b0100011 #jalr opcode
        tokens[0][7:13] = self.rd.num
        tokens[0][13:19] = self.rs1.num
        tokens[0][19:30] = self.offset
        # tokens[0][30] = 0b0 #start of new packet
        # tokens[0][31] = 0b1 #end of new packet
        return tokens[0].encode()


#btype instructions
class TwigBInstruction(Instruction):
    tokens = [TwigBToken]
    isa = isa

    #TODO: remove functionality for relocation from arch
    #def relocations(self):

def make_b(mnemonic, opcode):
    rd = Operand("rd", int)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    pred = Operand("pred", int)
    # pred  = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, ",", " ", pred])
    tokens = [TwigBToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
    }
    return type(mnemonic + "_ins", (TwigBInstruction,), members)

def make_pb(mnemonic, opcode):
    # pred = Operand("pred", str) # CHANGE TO INT LATER
    cur_pred = Operand("cur_pred", int)
    target = Operand("target", str)
    # pred  = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False

    syntax = Syntax([mnemonic, " ", "p", cur_pred, ",", " ", target])
        # syntax = Syntax([mnemonic, " ", pred, ",", " ", target])

    tokens = [TwigBToken]
    patterns = {
        # "pred": pred,
        "cur_pred": cur_pred,
        "target": target
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        # "pred": pred,
        "cur_pred": cur_pred,
        "target": target,
        # "pstart": pstart,
        # "pend": pend,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
    }
    return type(mnemonic + "_ins", (TwigBInstruction,), members)

def make_sb(mnemonic, opcode):
    pred = Operand("pred", int)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    # pred  = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", pred, ",", " ", rs1, ",", " ", rs2])
    tokens = [TwigBToken]
    patterns = {
        "opcode": opcode,
        "pred": pred,
        "rs1": rs1,
        "rs2": rs2
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "pred": pred,
        "rs1": rs1,
        "rs2": rs2,
        # "pstart": pstart,
        # "pend": pend,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
    }
    return type(mnemonic + "_ins", (TwigBInstruction,), members)

Jpnz = make_pb("jpnz", 0b1100000)

Beq = make_b("beq", 0b1000000)
Bne = make_b("bne", 0b1000001)
Bge = make_b("bge", 0b1000010)
Bgeu = make_b("bgeu", 0b1000011)
Blt = make_b("blt", 0b1000100)
Bltu = make_b("bltu", 0b1000101)
Beqf = make_b("beqf", 0b1001000)
Bnef = make_b("bnef", 0b1001001)
Bgef = make_b("bgef", 0b1001010)
Bltf = make_b("bltf", 0b1001100)

#u type
class TwigUInstruction(Instruction):
    tokens = [TwigUToken]
    isa = isa

def make_u(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    imm = Operand("imm", int)
    pred = Operand("pred", int)
    syntax = Syntax([mnemonic, ",", " ", rd, ",", " ", imm, ",", " ", pred])
    tokens = [TwigUToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "imm": imm,
        "pred": pred
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "imm": imm,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
        "pred": pred
    }
    return type(mnemonic + "_ins", (TwigUInstruction,), members)

def make_u_mod(mnemonic, opcode):
    """
    Creates a U-type instruction that MODIFIES rd
    (reads and writes it).
    """
    rd = Operand("rd", TwigRegister, read=True, write=True)
    imm = Operand("imm", int)
    pred = Operand("pred", int)
    syntax = Syntax([mnemonic, ",", " ", rd, ",", " ", imm, ",", " ", pred])
    tokens = [TwigUToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "imm": imm,
        "pred": pred
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "imm": imm,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
        "pred": pred
    }
    return type(mnemonic + "_ins", (TwigUInstruction,), members)

Auipc = make_u("auipc", 0b1010000)
Lli = make_u_mod("lli", 0b1010001)
Lmi = make_u_mod("lmi", 0b1010010)
Lui = make_u("lui", 0b1010011)

#h type (halt)
class TwigHInstruction(Instruction):
    tokens = [TwigHToken]
    isa = isa

def make_nop(mnemonic, opcode):
    # pred  = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    # syntax = Syntax([mnemonic, ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic])
    tokens = [TwigHToken]
    patterns = {
        "opcode": opcode
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    return type(mnemonic + "_ins", (TwigHInstruction,), members)

Halt = make_nop("halt", 0b1111111)

class PseudoTwigInstruction(ArtificialInstruction):
    isa = isa
    pass

class Align(PseudoTwigInstruction):
    imm = Operand("imm", int)
    syntax = Syntax([".", "align", " ", imm])

    def render(self):
        self.rep = self.syntax.render(self)
        yield Alignment(self.imm, self.rep)

class Section(PseudoTwigInstruction):
    sec = Operand("sec", str)
    syntax = Syntax([".", "section", " ", sec])

    def render(self):
        self.rep = self.syntax.render(self)
        yield SectionInstruction(self.sec, self.rep)

def dcd(v):
    if type(v) is int:
        return Dd(v)
    elif type(v) is str:
        return Dcd2(v)
    else:  # pragma: no cover
        raise NotImplementedError()

#isa.pattern stuff

#pattern to look for: return "reg", format: ADD Unsigned 32 bit with 2 children that are registers, size/cost: 2

#add pattern
@isa.pattern("reg", "ADDU32(reg,reg)", size=2)
@isa.pattern("reg", "ADDI32(reg,reg)", size=2)
def pattern_add_i32(context, tree, c0, c1): #c0 = rs1, c1 = rs2, d = rd
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Add(d,c0,c1, p))
    return d

@isa.pattern("reg", "ADDU16(reg, reg)", size=2)
@isa.pattern("reg", "ADDI16(reg, reg)", size=2)
def pattern_add_i16(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Add(d, c0, c1, p))
    return d

@isa.pattern("reg", "ADDI8(reg, reg)", size=2)
@isa.pattern("reg", "ADDU8(reg, reg)", size=2)
def pattern_add8(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Add(d, c0, c1, p))
    return d


#f patterns
@isa.pattern("reg", "I32TOF32(reg)", size=2)
@isa.pattern("reg", "U32TOF32(reg)", size=2)
def pattern_int_to_float(context, tree, c0):
    """
    Matches an (int -> float) or (unsigned -> float) cast.
    'c0' is the register holding the integer.
    Emits the 'itof' hardware instruction.
    """
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(ItoF(d, c0, p))
    return d


def call_internal1(context, name, a, pred, clobbers=()):
    from .registers import R10, R12, LR
    d = context.new_reg(TwigRegister)
    context.emit(Addi(R12, a, 0, pred))
    context.emit(RegisterUseDef(uses=(R12,)))
    context.emit(Global(name))
    context.emit(Bl(LR, name, clobbers=clobbers))
    context.emit(RegisterUseDef(uses=(R10,)))
    context.move(Addi(d, R10, 0, pred))
    return d

# @isa.pattern("reg", "NEGF64(reg)", size=20)
@isa.pattern("reg", "NEGF32(reg)", size=20)
def pattern_neg_f32(context, tree, c0):
    return call_internal1(
        context, "float32_neg", c0, tree.pred, clobbers=context.arch.caller_save
    )

# @isa.pattern("reg", "F64TOF32(reg)", size=10)
def pattern_i32_to_i32(context, tree, c0):
    return c0

@isa.pattern("reg", "F32TOI32(reg)", size=2)
@isa.pattern("reg", "F32TOU32(reg)", size=2)
def pattern_float_to_int(context, tree, c0):
    """
    Matches a (float -> int) or (float -> unsigned) cast.
    'c0' is the register holding the float.
    Emits the 'ftoi' hardware instruction.
    """
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(FtoI(d, c0, p))
    return d

@isa.pattern("reg", "ADDF32(reg, reg)", size=2)
def pattern_add_f32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Addf(d, c0, c1, p))
    return d

@isa.pattern("reg", "SUBF32(reg, reg)", size=2)
def pattern_sub_f32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Subf(d, c0, c1, p))
    return d

@isa.pattern("reg", "MULF32(reg, reg)", size=4)
def pattern_mul_f32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Mulf(d, c0, c1, p))
    return d

@isa.pattern("reg", "DIVF32(reg, reg)", size=8)
def pattern_div_f32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Divf(d, c0, c1, p))
    return d

@isa.pattern("reg", "LDRF32(mem)", size=2)
def pattern_ldr_f32_mem(context, tree, c0):
    """ Matches: float x = stack_var; """
    d = context.new_reg(TwigRegister)
    base_reg, offset = c0
    p = tree.pred
    Code = Lw(d, offset, base_reg, p)
    Code.fprel = True
    context.emit(Code)
    return d

@isa.pattern("reg", "LDRF32(reg)", size=2)
def pattern_ldr_f32_reg(context, tree, c0):
    """ Matches: float x = *float_pointer; """
    d = context.new_reg(TwigRegister)
    base_reg = c0
    p = tree.pred
    Code = Lw(d, 0, base_reg, p)
    context.emit(Code)
    return d

#'j' pattern
@isa.pattern("stm", "JMP", size=4)
def pattern_jmp(context, tree):
    tgt = tree.value
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))



@isa.pattern(
    "reg",
    "FPRELU32",
    size=4,
    condition=lambda t: t.value.offset in range(-32, 32),
)
def pattern_fpreli32(context, tree):
    d = context.new_reg(TwigRegister)
    offset = tree.value.offset
    p = tree.pred
    Code = Addi(d, FP, offset, p)
    Code.fprel = True
    context.emit(Code)
    return d


# Memory patterns:
@isa.pattern(
    "mem",
    "FPRELU32",
    size=0,
    condition=lambda t: t.value.offset in range(-32, 32),
)
def pattern_mem_fpreli32(context, tree):
    offset = tree.value.offset
    return FP, offset


@isa.pattern(
    "reg",
    "FPRELU32",
    size=10
)
def pattern_fprel_large(context, tree):
    """
    Handles FPREL (stack variable) when the offset is too
    large for a 6-bit immediate.

    It loads the offset into a temp register and adds it to FP.
    """
    offset = tree.value.offset
    p = tree.pred
    t1 = context.new_reg(TwigRegister)
    if offset in range(-32, 32):

        context.emit(Addi(t1, R0, offset, p))
    else:
        upper_8 = (offset >> 24) & 0xFF
        middle_12 = (offset >> 12) & 0xFFF
        lower_12 = (offset) & 0xFFF
        context.emit(Lui(t1, upper_8, p))
        context.emit(Lmi(t1, middle_12, p))
        context.emit(Lli(t1, lower_12, p))

    d = context.new_reg(TwigRegister)
    context.emit(Add(d, FP, t1, p))
    return d

@isa.pattern("mem", "reg", size=10)
def pattern_mem_reg(context, tree, c0):
    return c0, 0

#sw pattern
@isa.pattern("stm", "STRU32(mem, reg)", size=2)
@isa.pattern("stm", "STRI32(mem, reg)", size=2)
@isa.pattern("stm", "STRF32(mem, reg)", size=10)
# @isa.pattern("stm", "STRF64(mem, reg)", size=10)
def pattern_sw32(context, tree, c0, c1):
    base_reg, offset = c0
    p = tree.pred
    Code = Sw(c1, offset, base_reg, p)
    Code.fprel = True
    context.emit(Code)

@isa.pattern("stm", "STRU32(reg, reg)", size=2)
@isa.pattern("stm", "STRI32(reg, reg)", size=2)
@isa.pattern("stm", "STRF32(reg, reg)", size=10)
# @isa.pattern("stm", "STRF64(reg, reg)", size=10)
def pattern_sw32_reg(context, tree, c0, c1):
    base_reg = c0
    p = tree.pred
    Code = Sw(c1, 0, base_reg, p)
    context.emit(Code)


@isa.pattern("stm", "STRI16(mem, reg)", size=2)
@isa.pattern("stm", "STRU16(mem, reg)", size=2)
def pattern_str16_mem(context, tree, c0, c1):
    base_reg, offset = c0
    p = tree.pred
    Code = Sh(c1, offset, base_reg, p)
    Code.fprel = True
    context.emit(Code)


@isa.pattern("stm", "STRI16(reg, reg)", size=2)
@isa.pattern("stm", "STRU16(reg, reg)", size=2)
def pattern_str16_reg(context, tree, c0, c1):
    base_reg = c0
    p = tree.pred
    Code = Sh(c1, 0, base_reg, p)
    context.emit(Code)


@isa.pattern("stm", "STRU8(mem, reg)", size=2)
@isa.pattern("stm", "STRI8(mem, reg)", size=2)
def pattern_sbi8_mem(context, tree, c0, c1):
    base_reg, offset = c0
    p = tree.pred
    Code = Sb(c1, offset, base_reg, p)
    Code.fprel = True
    context.emit(Code)


@isa.pattern("stm", "STRU8(reg, reg)", size=2)
@isa.pattern("stm", "STRI8(reg, reg)", size=2)
def pattern_sbi8_reg(context, tree, c0, c1):
    base_reg = c0
    p = tree.pred
    Code = Sb(c1, 0, base_reg, p)
    context.emit(Code)


@isa.pattern("reg", "CONSTI32", size=4)
@isa.pattern("reg", "CONSTU32", size=4)
def pattern_const(context, tree):
    d = context.new_reg(TwigRegister)
    c0 = tree.value
    p = tree.pred
    if c0 in range(-32, 32):
        context.emit(Addi(d, R0, c0, p))
        return d
    upper_8 = (c0 >> 24) & 0xFF
    middle_12 = (c0 >> 12) & 0xFFF
    lower_12 = (c0) & 0xFFF
    context.emit(Lui(d,upper_8, p))
    context.emit(Lmi(d,middle_12, p))
    context.emit(Lli(d,lower_12, p))
    return d

@isa.pattern("stm", "MOVI32(reg)", size=2)
@isa.pattern("stm", "MOVU32(reg)", size=2)
@isa.pattern("stm", "MOVF32(reg)", size=2)
def pattern_mov32(context, tree, c0):
    # context.move(tree.value, c0)
    dst = tree.value
    src = c0
    p = tree.pred
    context.emit(Addi(dst, src, 0, p))
    return dst

@isa.pattern("reg", "LDRU32(mem)", size=2)
@isa.pattern("reg", "LDRI32(mem)", size=2)
def pattern_ldr32_fprel(context, tree, c0):
    d = context.new_reg(TwigRegister)
    base_reg, offset = c0
    p = tree.pred
    Code = Lw(d, offset, base_reg, p)
    Code.fprel = True
    context.emit(Code)
    return d


@isa.pattern("reg", "LDRU32(reg)", size=2)
@isa.pattern("reg", "LDRI32(reg)", size=2)
def pattern_ldr32_reg(context, tree, c0):
    d = context.new_reg(TwigRegister)
    base_reg = c0
    p = tree.pred
    Code = Lw(d, 0, base_reg, p)
    context.emit(Code)
    return d

@isa.pattern("reg", "REGI32", size=0)
@isa.pattern("reg", "REGU32", size=0)
@isa.pattern("reg", "REGF32", size=0)
def pattern_reg(context, tree):
    return tree.value


@isa.pattern("stm", "MOVB(reg, reg)", size=40)
def pattern_movb(context, tree, c0, c1):
    # Emit memcpy
    dst = c0
    src = c1
    tmp = context.new_reg(TwigRegister)
    size = tree.value
    p = tree.pred
    for instruction in context.arch.gen_twig_memcpy(dst, src, tmp, size, pred=p):
        context.emit(instruction)

@isa.pattern("reg", "U32TOU16(reg)", size=0)
@isa.pattern("reg", "U32TOI16(reg)", size=0)
@isa.pattern("reg", "I32TOI16(reg)", size=0)
@isa.pattern("reg", "I32TOU16(reg)", size=0)
@isa.pattern("reg", "U16TOU8(reg)", size=0)
@isa.pattern("reg", "U16TOI8(reg)", size=0)
@isa.pattern("reg", "I16TOI8(reg)", size=0)
@isa.pattern("reg", "I16TOU8(reg)", size=0)
# @isa.pattern("reg", "F32TOF64(reg)", size=10)
@isa.pattern("reg", "F32TOF32(reg)", size=10)
def pattern_i32_to_i32(context, tree, c0):
    return c0

@isa.pattern("reg", "I8TOI16(reg)", size=4)
@isa.pattern("reg", "I8TOI32(reg)", size=4)
def pattern_i8_to_i32(context, tree, c0):
    p = tree.pred
    context.emit(Slli(c0, c0, 24, p))
    context.emit(Srai(c0, c0, 24, p))
    return c0


@isa.pattern("reg", "I16TOI32(reg)", size=4)
def pattern_i16_to_i32(context, tree, c0):
    p = tree.pred
    context.emit(Slli(c0, c0, 16, p))
    context.emit(Srai(c0, c0, 16, p))
    return c0

@isa.pattern("reg", "I8TOU16(reg)", size=4)
@isa.pattern("reg", "U8TOU16(reg)", size=4)
@isa.pattern("reg", "U8TOI16(reg)", size=4)
def pattern_8_to_16(context, tree, c0):
    p = tree.pred
    context.emit(Slli(c0, c0, 24, p))
    context.emit(Srli(c0, c0, 24, p))
    return c0

@isa.pattern("reg", "I8TOU32(reg)", size=4)
@isa.pattern("reg", "U8TOU32(reg)", size=4)
@isa.pattern("reg", "U8TOI32(reg)", size=4)
def pattern_8_to_32(context, tree, c0):
    p = tree.pred
    context.emit(Slli(c0, c0, 24, p))
    context.emit(Srli(c0, c0, 24, p))
    return c0


@isa.pattern("reg", "I16TOU32(reg)", size=4)
@isa.pattern("reg", "U16TOU32(reg)", size=4)
@isa.pattern("reg", "U16TOI32(reg)", size=4)
def pattern_16_to_32(context, tree, c0):
    p = tree.pred
    context.emit(Slli(c0, c0, 16, p))
    context.emit(Srli(c0, c0, 16, p))
    return c0

@isa.pattern("reg", "I32TOI8(reg)", size=0)
@isa.pattern("reg", "I32TOU8(reg)", size=0)
@isa.pattern("reg", "I32TOI16(reg)", size=0)
@isa.pattern("reg", "I32TOU16(reg)", size=0)
@isa.pattern("reg", "U32TOU8(reg)", size=0)
@isa.pattern("reg", "U32TOI8(reg)", size=0)
@isa.pattern("reg", "U32TOU16(reg)", size=0)
@isa.pattern("reg", "U32TOI16(reg)", size=0)
def pattern_32_to_8_16(context, tree, c0):
    # TODO: do something like sign extend or something else?
    return c0


@isa.pattern("reg", "CONSTF32", size=10)
# @isa.pattern("reg", "CONSTF64", size=10)
def pattern_const_f32(context, tree):
    float_const = struct.pack("f", tree.value)
    p = tree.pred
    (c0,) = struct.unpack("i", float_const)
    d = context.new_reg(TwigRegister)
    upper_8 = (c0 >> 24) & 0xFF
    middle_12 = (c0 >> 12) & 0xFFF
    lower_12 = (c0) & 0xFFF
    context.emit(Lui(d,upper_8,p))
    context.emit(Lmi(d,middle_12,p))
    context.emit(Lli(d,lower_12,p))
    return d

@isa.pattern("stm", "PJMP(reg, CONSTI32)", size=6)
def pattern_pjmp(context, tree):
    cur_pred, lab_yes, lab_no = tree.value
    context.emit(Jpnz(cur_pred, lab_yes.name))
    context.emit(Bl(R0, lab_no.name, jumps=[lab_no]))

# @isa.pattern("stm", "BJMPF64(reg,reg)", size=10)
@isa.pattern("stm", "BJMPF32(reg,reg)", size=10)
def pattern_bjmpf(context, tree, c0, c1):
    op, yes_label, no_label, yes_pred, no_pred, parent_pred = tree.value

    opnames = {"<": Bltf,
               ">": Bltf,
               "==": Beqf,
               "!=": Bnef,
               ">=": Bgef,
               "<=": Bgef
    }
    invops = {
                "<": Bgef,
                ">": Bgef,
                "==": Bnef,
                "!=": Beqf,
                ">=": Bltf,
                "<=": Bltf
    }
    invBop = invops[op]
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    context.emit(invBop(no_pred, c0, c1, parent_pred))
    tgt = yes_label
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

# @isa.pattern("stm", "BJMPI8(reg, reg)", size=10)
@isa.pattern("stm", "BJMPI16(reg, reg)", size=10)
@isa.pattern("stm", "BJMPI32(reg, reg)", size=10)
def pattern_bjmp(context, tree, c0, c1):
    # print(tree.value)
    # print((c0, c1))
    op, yes_label, no_label, yes_pred, no_pred, parent_pred = tree.value
    opnames = {"<": Blt,
               ">": Blt,
               "==": Beq,
               "!=": Bne,
               ">=": Bge,
               "<=": Bge
               }
    invops = {"<": Bge,
             ">": Bge,
             "==": Bne,
             "!=": Beq,
             ">=": Blt,
             "<=":  Blt
    }
    invBop = invops[op]
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    context.emit(invBop(no_pred, c0, c1, parent_pred))
    tgt = yes_label
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

@isa.pattern("stm", "BJMPU8(reg, reg)", size=10)
@isa.pattern("stm", "BJMPU16(reg, reg)", size=10)
@isa.pattern("stm", "BJMPU32(reg, reg)", size=10)
def pattern_bjmp(context, tree, c0, c1):
    # print(tree.value)
    # print((c0, c1))
    op, yes_label, no_label, yes_pred, no_pred, parent_pred = tree.value
    opnames = {"<": Bltu,
               ">": Bltu,
               "==": Beq,
               "!=": Bne,
               ">=": Bgeu,
               "<=": Bgeu
               }
    invops = {"<": Bgeu,
             ">": Bgeu,
             "==": Bne,
             "!=": Beq,
             ">=": Bltu,
             "<=":  Bltu
    }
    invBop = invops[op]
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    context.emit(invBop(no_pred, c0, c1, parent_pred))
    tgt = yes_label
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

@isa.pattern("stm", "SJMPU8(reg, reg)", size=10)
@isa.pattern("stm", "SJMPU16(reg, reg)", size=10)
@isa.pattern("stm", "SJMPU32(reg, reg)", size=10)
def pattern_sjmp(context, tree, c0, c1):
    op, yes_label, yes_pred, parent_pred = tree.value
    opnames = {"<": Bltu,
               ">": Bltu,
               "==": Beq,
               "!=": Bne,
               ">=": Bgeu,
               "<=": Bgeu
               }
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    tgt = yes_label #start by jumping to if, if needs to jump to else after (covered by gen_if)
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

@isa.pattern("stm", "SJMPI8(reg, reg)", size=10)
@isa.pattern("stm", "SJMPI16(reg, reg)", size=10)
@isa.pattern("stm", "SJMPI32(reg, reg)", size=10)
def pattern_sjmp(context, tree, c0, c1):
    op, yes_label, yes_pred, parent_pred = tree.value
    opnames = {"<": Blt,
               ">": Blt,
               "==": Beq,
               "!=": Bne,
               ">=": Bge,
               "<=": Bge
               }
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    tgt = yes_label
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

@isa.pattern("stm", "SJMPF32(reg, reg)", size=10)
def pattern_sjmp(context, tree, c0, c1):
    op, yes_label, yes_pred, parent_pred = tree.value
    opnames = {"<": Bltf,
               ">": Bltf,
               "==": Beqf,
               "!=": Bnef,
               ">=": Bgef,
               "<=": Bgef
               }
    Bop = opnames[op]
    if op == ">" or op == "<=":
        temp = c0
        c0 = c1
        c1 = temp
    context.emit(Bop(yes_pred, c0, c1, parent_pred))
    tgt = yes_label
    context.emit(Bl(R0, tgt.name, jumps=[tgt]))

@isa.pattern(
    "reg",
    "ADDI32(reg, CONSTI32)",
    size=2,
    condition=lambda t: t[1].value < 32,
)
@isa.pattern(
    "reg",
    "ADDU32(reg, CONSTU32)",
    size=2,
    condition=lambda t: t[1].value < 32,
)
def pattern_add_i32_reg_const(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[1].value
    p = tree.pred
    context.emit(Addi(d, c0, c1, p))
    return d

@isa.pattern(
    "reg",
    "ADDI32(CONSTI32, reg)",
    size=2,
    condition=lambda t: t.children[0].value < 32,
)
@isa.pattern(
    "reg",
    "ADDU32(CONSTU32, reg)",
    size=2,
    condition=lambda t: t.children[0].value < 323,
)
def pattern_add_i32_const_reg(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[0].value
    p = tree.pred
    context.emit(Addi(d, c0, c1, p))
    return d

@isa.pattern("reg", "SUBI8(reg, reg)", size=2)
@isa.pattern("reg", "SUBU8(reg, reg)", size=2)
@isa.pattern("reg", "SUBI16(reg, reg)", size=2)
@isa.pattern("reg", "SUBU16(reg, reg)", size=2)
@isa.pattern("reg", "SUBI32(reg, reg)", size=2)
@isa.pattern("reg", "SUBU32(reg, reg)", size=2)
def pattern_sub_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Sub(d, c0, c1, p))
    return d


#for labelling different blocks i assume
# @isa.pattern("reg", "LABEL", size=6)
# def pattern_label1(context, tree):
#     d = context.new_reg(RiscvRegister)
#     ln = context.frame.add_constant(tree.value)
#     context.emit(Adru(d, ln))
#     context.emit(Adrl(d, d, ln))
#     context.emit(Lw(d, 0, d))
#     return d


# @isa.pattern("reg", "LABEL", size=4)
# def pattern_label2(context, tree):
#     d = context.new_reg(RiscvRegister)
#     ln = context.frame.add_constant(tree.value)
#     context.emit(Labelrel(d, ln))
#     return d

@isa.pattern("reg", "NEGI8(reg)", size=2)
@isa.pattern("reg", "NEGI16(reg)", size=2)
@isa.pattern("reg", "NEGI32(reg)", size=2)
@isa.pattern("reg", "NEGU32(reg)", size=2)
def pattern_negi32(context, tree, c0):
    p = tree.pred
    context.emit(Sub(c0, R0, c0, p))
    return c0

@isa.pattern("reg", "INVI8(reg)", size=2)
@isa.pattern("reg", "INVU8(reg)", size=2)
@isa.pattern("reg", "INVU32(reg)", size=2)
@isa.pattern("reg", "INVI32(reg)", size=2)
def pattern_inv(context, tree, c0):
    p = tree.pred
    context.emit(Xori(c0, c0, -1, p))
    return c0

@isa.pattern("reg", "ANDI8(reg, reg)", size=2)
@isa.pattern("reg", "ANDU8(reg, reg)", size=2)
@isa.pattern("reg", "ANDI16(reg, reg)", size=2)
@isa.pattern("reg", "ANDU16(reg, reg)", size=2)
@isa.pattern("reg", "ANDI32(reg, reg)", size=2)
@isa.pattern("reg", "ANDU32(reg, reg)", size=2)
def pattern_and_i(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(And(d, c0, c1, p))
    return d

@isa.pattern("reg", "ORU32(reg, reg)", size=2)
@isa.pattern("reg", "ORI32(reg, reg)", size=2)
@isa.pattern("reg", "ORU16(reg, reg)", size=2)
@isa.pattern("reg", "ORI16(reg, reg)", size=2)
@isa.pattern("reg", "ORU8(reg, reg)", size=2)
@isa.pattern("reg", "ORI8(reg, reg)", size=2)
def pattern_or_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Or(d, c0, c1, p))
    return d


@isa.pattern(
    "reg",
    "ORI32(reg, CONSTI32)",
    size=2,
    condition=lambda t: t.children[1].value < 32,
)
def pattern_or_i32_reg_const(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[1].value
    p = tree.pred
    context.emit(Ori(d, c0, c1, p))
    return d

@isa.pattern(
    "reg",
    "ORI32(CONSTI32, reg)",
    size=2,
    condition=lambda t: t.children[0].value < 32,
)
def pattern_or_i32_const_reg(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[0].value
    p = tree.pred
    context.emit(Ori(d, c0, c1, p))
    return d

@isa.pattern("reg", "SHRU8(reg, reg)", size=2)
@isa.pattern("reg", "SHRU16(reg, reg)", size=2)
@isa.pattern("reg", "SHRU32(reg, reg)", size=2)
def pattern_shr_u32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Srl(d, c0, c1, p))
    return d


@isa.pattern("reg", "SHRI8(reg, reg)", size=2)
def pattern_shr_i8(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Slli(c0, c0, 24, p))
    context.emit(Srai(c0, c0, 24, p))
    context.emit(Sra(d, c0, c1, p))
    return d


@isa.pattern("reg", "SHRI16(reg, reg)", size=2)
def pattern_shr_i16(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Slli(c0, c0, 16, p))
    context.emit(Srai(c0, c0, 16, p))
    context.emit(Sra(d, c0, c1, p))
    return d


@isa.pattern("reg", "SHRI32(reg, reg)", size=2)
def pattern_shr_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Sra(d, c0, c1, p))
    return d


@isa.pattern(
    "reg",
    "SHRI32(reg, CONSTI32)",
    size=2,
    condition=lambda t: t.children[1].value < 32,
)
def pattern_shr_i32_reg_const(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[1].value
    p = tree.pred
    context.emit(Srai(d, c0, c1, p))
    return d


@isa.pattern("reg", "SHLU8(reg, reg)", size=2)
@isa.pattern("reg", "SHLI8(reg, reg)", size=2)
@isa.pattern("reg", "SHLU16(reg, reg)", size=2)
@isa.pattern("reg", "SHLI16(reg, reg)", size=2)
@isa.pattern("reg", "SHLU32(reg, reg)", size=2)
@isa.pattern("reg", "SHLI32(reg, reg)", size=2)
def pattern_shl_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Sll(d, c0, c1, p))
    return d

@isa.pattern(
    "reg",
    "SHLI32(reg, CONSTI32)",
    size=2,
    condition=lambda t: t.children[1].value < 32,
)
def pattern_shl_i32_reg_const(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[1].value
    p = tree.pred
    context.emit(Slli(d, c0, c1, p))
    return d

@isa.pattern("reg", "MULI8(reg, reg)", size=10)
@isa.pattern("reg", "MULU8(reg, reg)", size=10)
@isa.pattern("reg", "MULU16(reg, reg)", size=10)
@isa.pattern("reg", "MULI32(reg, reg)", size=10)
@isa.pattern("reg", "MULU32(reg, reg)", size=10)
def pattern_mul_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Mul(d, c0, c1, p))
    return d

@isa.pattern("reg", "DIVI32(reg, reg)", size=10)
def pattern_div_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Div(d, c0, c1, p))
    return d

#there better not be unsigned division
@isa.pattern("reg", "DIVU16(reg, reg)", size=10)
@isa.pattern("reg", "DIVU32(reg, reg)", size=10)
def pattern_div_u32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Div(d, c0, c1, p))
    return d

#if there is many modulo maybe separate instruction would be good
@isa.pattern("reg", "REMI32(reg, reg)", size=14)
@isa.pattern("reg", "REMU32(reg, reg)", size=14)
def pattern_rem32(context, tree, c0, c1):
    """
    Implements Remainder (c0 % c1) using the formula:
    d = c0 - (c1 * (c0 / c1))
    """
    t1 = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Div(t1, c0, c1, p))
    t2 = context.new_reg(TwigRegister)
    context.emit(Mul(t2, c1, t1, p))
    d = context.new_reg(TwigRegister)
    context.emit(Sub(d, c0, t2, p))
    return d

@isa.pattern("reg", "XORU32(reg, reg)", size=2)
@isa.pattern("reg", "XORI32(reg, reg)", size=2)
def pattern_xor_i32(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    p = tree.pred
    context.emit(Xor(d, c0, c1, p))
    return d

@isa.pattern(
    "reg",
    "XORI32(reg, CONSTI32)",
    size=2,
    condition=lambda t: t.children[1].value < 32,
)
def pattern_xor_i32_reg_const(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[1].value
    p = tree.pred
    context.emit(Xori(d, c0, c1, p))
    return d

@isa.pattern(
    "reg",
    "XORI32(CONSTI32, reg)",
    size=2,
    condition=lambda t: t.children[0].value < 32,
)
def pattern_xor_i32_const_reg(context, tree, c0):
    d = context.new_reg(TwigRegister)
    c1 = tree.children[0].value
    p = tree.pred
    context.emit(Xori(d, c0, c1, p))
    return d


#legacy code grandfathered in since May 22, 2019 at 10:33 AM
def round_up(s):
    return s + (16 - s % 16)
