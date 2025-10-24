from ..isa import Isa
from ..encoding import Instruction, Operand, Syntax
from .tokens import *
from .registers import (
    TwigRegister, TwigPredRegister
)

isa = Isa()

class TwigRInstruction(Instruction):
    tokens = [TwigRToken]
    isa = isa

def make_r(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    rs1 = Operand("rs1", TwigRegister, read=True)
    rs2 = Operand("rs2", TwigRegister, read=True)
    pred = Operand("pred", TwigPredRegister, read=True)
    pstart = Operand("pstart", int, read=True)
    pend = Operand("pend", int, read=True)
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    tokens = [TwigRToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        "pstart": pstart,
        "pend": pend
    }
    members = {
        "syntax": syntax,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        "pstart": pstart,
        "pend": pend,
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
    pred = Operand("pred", TwigPredRegister, read=True)
    pstart = Operand("pstart", int, read=True)
    pend = Operand("pend", int, read=True)
    fprel = False
    tokens = [TwigIToken]
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", offset, " ", pred, ",", " ", pstart, ",", " ", pend])
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        "pstart": pstart,
        "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "offset": offset,
        "pred": pred,
        "pstart": pstart,
        "pend": pend,
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

#lw, lh, lb, are different "I Type"
#jalr should not be Itype, should be P type

#loads
def make_load(mnemonic, opcode):
    rd = Operand("rd", TwigRegister, write=True)
    offset = Operand("offset", int)
    rs1 = Operand("rs1", TwigRegister, read=True)
    pred = Operand("pred", TwigPredRegister, read=True)
    pstart = Operand("pstart", int, read=True)
    pend = Operand("pend", int, read=True)
    fprel = False
    syntax = Syntax([mnemonic, " ", rd, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    tokens = [TwigIToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        "pstart": pstart,
        "pend": pend
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
        "pstart": pstart,
        "pend": pend,
        "opcode": opcode
    }
    return type(mnemonic.title(), (TwigIInstruction), members)

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
    pred = Operand("pred", TwigPredRegister, read=True)
    pstart = Operand("pstart", int, read=True)
    pend = Operand("pend", int, read=True)
    fprel = False
    syntax = Syntax([mnemonic, " ", rs2, ",", " ", offset, "(", rs1, ")", ",", " ", pred, ",", " ", pstart, ",", " ", pend])
    tokens = [TwigSToken]
    patterns = {
        "opcode": opcode,
        "rs2": rs2,
        "rs1": rs1,
        "imm": offset,
        "pred": pred,
        "pstart": pstart,
        "pend": pend
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
        "pstart": pstart,
        "pend": pend,
        "opcode": opcode
    }
    return type(mnemonic.title(), (TwigSInstruction), members)

Sw = make_store("sw", 0b0110000)
Sh = make_store("sh", 0b0110001)
Sb = make_store("sb", 0b0110010)


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
    pred  = Operand("pred", TwigPredRegister, read=True)
    pstart = Operand("pstart", int, read=True)
    pend = Operand("pend", int, read=True)
    fprel = False
    syntax = Syntax([mnemonic, " ", rd, ",", " ", rs1, ",", " ", rs2, " ", pred, ",", " ", pstart, ",", " ", pend])
    tokens = [TwigBToken]
    patterns = {
        "opcode": opcode,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        "pstart": pstart,
        "pend": pend
    }
    members = {
        "syntax": syntax,
        "fprel": fprel,
        "rd": rd,
        "rs1": rs1,
        "rs2": rs2,
        "pred": pred,
        "pstart": pstart,
        "pend": pend,
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
