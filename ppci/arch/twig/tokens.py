from ..token import Token, bit, bit_concat, bit_range


class TwigRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(18,13)
    rs2 = bit_range(24,19)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigIToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(18,13)
    imm6 = bit_range(24,19)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigFToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(18,13)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigSToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    imm = bit_range(12,7)
    rs1 = bit_range(18,13)
    rs2 = bit_range(24,19)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigBToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(18,13)
    rs2 = bit_range(24,19)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigUToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    imm12 = bit_range(24,13)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigCWToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_concat(bit_range(22,19), bit_range(12,7))
    rs1 = bit_range(18,13)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigCRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(22,13)
    pred = bit_range(29,25)
    pstart = bit(30)
    pend = bit(31)

class TwigJToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    imm12 = bit_range(24,13)
    pstart = bit(30)
    pend = bit(31)

class TwigPToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rs1 = bit_range(18,13)
    rs2 = bit_range(24,19)
    pstart = bit(30)
    pend = bit(31)

#do we need halt token?
# class TwigHaltToken(Token):
#     class Info:
#         size = 32

#     opcode = bit_range(6,0)
#     pred = bit_range(29,25)
#     pstart = bit(30)
#     pend = bit(31)
