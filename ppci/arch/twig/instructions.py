from ..isa import Isa
from ..encoding import Instruction, Operand, Syntax
from .tokens import *
from .registers import (
    TwigRegister, TwigPredRegister, R0, FP
)
from .relocations import *

isa = Isa()

isa.register_relocation(JImm17Relocation)

class TwigRInstruction(Instruction):
    tokens = [TwigRToken]
    isa = isa

def make_r(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    # pred = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2])
    tokens = [TwigRToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        # "pred": pred,
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
    # pred = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    tokens = [TwigIToken]
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", offset, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", offset])
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "offset": offset,
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "tokens": tokens,
        "patterns": patterns,
        "opcode": opcode
    }
    return type(mnemonic + "_ins", (TwigIInstruction,), members)

Addi = make_i("addi", 0b0010000)
Subi = make_i("addi", 0b0010001)
Ori = make_i("addi", 0b0010101)
Slti = make_i("addi", 0b0010111)
Sltiu = make_i("addi", 0b0011000)
Srli = make_i("addi", 0b0011110)
Srai = make_i("addi", 0b0011111)

#loads
def make_load(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    offset = Operand("offset", int)
    rs1 = Operand("rs1", TwigRegister, read=True)
    # pred = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", offset, "(", rs1, ")",])
    tokens = [TwigIToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset
        # "pred": pred,
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
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "opcode": opcode
    }
    return type(mnemonic.title(), (TwigIInstruction,), members)

Lw = make_load("lw", 0b01000000)
Lh = make_load("lw", 0b01000001)
Lb = make_load("lw", 0b01000010)

class TwigSInstruction(Instruction):
    tokens = [TwigSToken]
    isa = isa

def make_store(mnemonic, opcode):
    rs1 = Operand("rs1", TwigRegister, read=True)
    offset = Operand("offset", int)
    rs2 = Operand("rs2", TwigRegister, read=True)
    # pred = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rs2, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rs2, ",", " ", offset, "(", rs1, ")"])
    tokens = [TwigSToken]
    patterns = {
        "opcode": opcode,
        "rs2": rs2,
        "rs1": rs1,
        "imm": offset
        # "pred": pred,
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
        # "pred": pred,
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

#jal
class Bl(TwigJInstruction):
    rd = Operand("rd", TwigRegister, write=True)
    target = Operand("target", str)
    syntax = Syntax(["jal", " ", rd, ",", " ", target])
    def encode(self):
        tokens = self.get_tokens()
        tokens[0][0:7] = 0b1100000 #jal opcode
        tokens[0][7:13] = self.rd.num
        # tokens[0][30] = 0b0 #start of new packet
        # tokens[0][31] = 0b1 # end of curr packet
        return tokens[0].encode()

    def relocations(self):
        return [JImm17Relocation]

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
    rd = Operand("rd", TwigPredRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    # pred  = Operand("pred", TwigPredRegister, read=True)
    # pstart = Operand("pstart", int, read=True)
    # pend = Operand("pend", int, read=True)
    fprel = False
    # syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2])
    tokens = [TwigBToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        # "pred": pred,
        # "pstart": pstart,
        # "pend": pend,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode,
    }
    return type(mnemonic + "_ins", (TwigBInstruction,), members)

Beq = make_b("beq", 0b1000000)
Bne = make_b("bne", 0b1000001)
Bge = make_b("bge", 0b1000010)
Bgeu = make_b("bgeu", 0b1000011)
Blt = make_b("blt", 0b1000100)
Bltu = make_b("bltu", 0b1000101)


#u type
class TwigUInstruction(Instruction):
    tokens = [TwigUToken]
    isa = isa

def make_u(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    imm = Operand("imm", int)
    syntax = Syntax([mnemonic, ",", " ", rd, ",", " ", imm])
    tokens = [TwigUToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "imm12": imm
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "imm12": imm,
        "patterns": patterns,
        "tokens": tokens,
        "opcode": opcode
    }
    return type(mnemonic + "_ins", (TwigUInstruction,), members)

Auipc = make_u("auipc", 0b1010000)
Lli = make_u("lli", 0b1010001)
Lmi = make_u("lmi", 0b1010010)
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


#isa.pattern stuff

#pattern to look for: return "reg", format: ADD Unsigned 32 bit with 2 children that are registers, size/cost: 2

#add pattern
@isa.pattern("reg", "ADDU32(reg,reg)", size=2)
@isa.pattern("reg", "ADDI32(reg,reg)", size=2)
def pattern_add_i32(context, tree, c0, c1): #c0 = rs1, c1 = rs2, d = rd
    d = context.new_reg(TwigRegister)
    context.emit(Add(d,c0,c1))
    return d

@isa.pattern("reg", "ADDU16(reg, reg)", size=2)
@isa.pattern("reg", "ADDI16(reg, reg)", size=2)
def pattern_add_i16(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    context.emit(Add(d, c0, c1))
    return d

@isa.pattern("reg", "ADDI8(reg, reg)", size=2)
@isa.pattern("reg", "ADDU8(reg, reg)", size=2)
def pattern_add8(context, tree, c0, c1):
    d = context.new_reg(TwigRegister)
    context.emit(Add(d, c0, c1))
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
    Code = Addi(d, FP, offset)
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
    Code = Sw(c1, offset, base_reg)
    Code.fprel = True
    context.emit(Code)

@isa.pattern("stm", "STRU32(reg, reg)", size=2)
@isa.pattern("stm", "STRI32(reg, reg)", size=2)
@isa.pattern("stm", "STRF32(reg, reg)", size=10)
# @isa.pattern("stm", "STRF64(reg, reg)", size=10)
def pattern_sw32_reg(context, tree, c0, c1):
    base_reg = c0
    Code = Sw(c1, 0, base_reg)
    context.emit(Code)


@isa.pattern("stm", "STRI16(mem, reg)", size=2)
@isa.pattern("stm", "STRU16(mem, reg)", size=2)
def pattern_str16_mem(context, tree, c0, c1):
    base_reg, offset = c0
    Code = Sh(c1, offset, base_reg)
    Code.fprel = True
    context.emit(Code)


@isa.pattern("stm", "STRI16(reg, reg)", size=2)
@isa.pattern("stm", "STRU16(reg, reg)", size=2)
def pattern_str16_reg(context, tree, c0, c1):
    base_reg = c0
    Code = Sh(c1, 0, base_reg)
    context.emit(Code)


@isa.pattern("stm", "STRU8(mem, reg)", size=2)
@isa.pattern("stm", "STRI8(mem, reg)", size=2)
def pattern_sbi8_mem(context, tree, c0, c1):
    base_reg, offset = c0
    Code = Sb(c1, offset, base_reg)
    Code.fprel = True
    context.emit(Code)


@isa.pattern("stm", "STRU8(reg, reg)", size=2)
@isa.pattern("stm", "STRI8(reg, reg)", size=2)
def pattern_sbi8_reg(context, tree, c0, c1):
    base_reg = c0
    Code = Sb(c1, 0, base_reg)
    context.emit(Code)


@isa.pattern("reg", "CONSTI32", size=4)
@isa.pattern("reg", "CONSTU32", size=4)
def pattern_const(context, tree):
    d = context.new_reg(TwigRegister)
    c0 = tree.value
    if c0 in range(-32, 32):
        context.emit(Addi(d, R0, c0))
        return d
    upper_8 = (c0 >> 24) & 0xFF
    middle_12 = (c0 >> 12) & 0xFFF
    lower_12 = (c0) & 0xFFF
    context.emit(Lui(d,upper_8))
    context.emit(Lmi(d,middle_12))
    context.emit(Lli(d,lower_12))
    return d
