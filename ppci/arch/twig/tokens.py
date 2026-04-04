from ..token import Token, bit_concat, bit_range


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


class TwigCToken(Token):
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


class TwigJpnzToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    prs = bit_range(7, 13)
    imm = bit_range(13, 25)     # imm[12:0] = {rs2[24:19], imm[18:13], 1'b0}
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)


class TwigPredSWToken(Token):
    """Token for predicate memory instructions (prsw/prlw).
    Stores/loads a predicate register to/from memory."""

    class Info:
        size = 32

    opcode = bit_range(0, 7)
    imm = bit_range(13, 19)  # 6 bits: signed offset
    rs2 = bit_range(19, 25)  # 6 bits: GPR base address
    prs = bit_range(25, 30)  # 5 bits: pred register index (P0-P31)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)

class TwigPredLWToken(Token):
    """Token for predicate memory instructions (prsw/prlw).
    Stores/loads a predicate register to/from memory."""

    class Info:
        size = 32

    opcode = bit_range(0, 7)
    prd = bit_range(7, 13)
    imm = bit_range(13, 19)  # 6 bits: signed offset
    rs2 = bit_range(19, 25)  # 6 bits: GPR base address
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)


class TwigHToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    data = bit_range(7, 25)
    pred = bit_range(25, 30)
    pstart = bit_range(30, 31)
    pend = bit_range(31, 32)
