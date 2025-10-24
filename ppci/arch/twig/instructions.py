from ..isa import Isa
from ..encoding import Instruction, Operand, Syntax
from .tokens import TwigRToken, TwigIToken, TwigFToken
from .tokens import TwigBToken, TwigSToken, TwigCRToken, TwigPToken
from .tokens import TwigUToken, TwigCRToken, TwigCWToken, TwigJToken
from .registers import (
    TwigRegister, TwigPredRegister
)

isa = Isa()

class TwigInstruction(Instruction):
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
    name = mnemonic.title() + "RegRegReg"
    return type(name, (TwigInstruction,), members)

# should change opcode ("inst", opcode) to binary (currently decimal)
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
