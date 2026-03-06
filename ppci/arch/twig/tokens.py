from ..token import Token, bit, bit_concat, bit_range


class TwigRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    rs2 = bit_range(19, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigIToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    imm = bit_range(19, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigFToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigSToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    imm = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    rs2 = bit_range(19, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigBToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    rs2 = bit_range(19, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigUToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    imm = bit_range(13, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigCWToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_concat(bit_range(19,23), bit_range(7,13))
    rs1 = bit_range(13,19)
    # pred = bit_range(25,30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigCRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 23)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigJToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    imm = bit_range(13, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigJrToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)
    imm = bit_range(19, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigPToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)

    # imm = {imm[29:25], rs2[24:19]}
    rs2 = bit_range(19, 25)
    imm = bit_range(25, 30)

    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

#using halt token as nop token
class TwigHToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    # pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)
