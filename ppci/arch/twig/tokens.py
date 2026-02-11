from ..token import Token, bit, bit_concat, bit_range


class TwigRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,19)
    rs2 = bit_range(19,25)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigIToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,19)
    imm = bit_range(19,25)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigFToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,19)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigSToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    imm = bit_range(7,13)
    rs1 = bit_range(13,19)
    rs2 = bit_range(19,25)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigBToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,19)
    rs2 = bit_range(19,25)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigUToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    imm = bit_range(13,25)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigCWToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_concat(bit_range(19,23), bit_range(7,13))
    rs1 = bit_range(13,19)
    # pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigCRToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,23)
    pred = bit_range(25,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigJToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    imm = bit_range(13,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigJrToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7,13)
    rs1 = bit_range(13,19)
    imm = bit_range(19,30)
    # pstart = bit(30)
    # pend = bit(31)

class TwigPToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    rd = bit_range(7, 13)
    rs1 = bit_range(13, 19)

    # imm = {imm[29:25], rs2[24:19]}
    rs2 = bit_range(19, 25)
    imm = bit_range(25, 30)

    # pstart = bit(30)
    # pend = bit(31)

class TwigPredLWToken(Token):
    """Token for predicate memory instructions (prsw/prlw).
    Stores/loads a predicate register to/from memory."""
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    prd = bit_range(7, 12)
    rs2 = bit_range(19, 25)    # 6 bits: GPR base address
    imm = bit_range(13, 19)    # 6 bits: signed offset

class TwigPredSWToken(Token):
    """Token for predicate memory instructions (prsw/prlw).
    Stores/loads a predicate register to/from memory."""
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    prs = bit_range(25, 30)     # 5 bits: pred register index (P0-P31)
    rs2 = bit_range(19, 25)    # 6 bits: GPR base address
    imm = bit_range(13, 19)    # 6 bits: signed offset

#using halt token as nop token
class TwigHToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0,7)
    # pred = bit_range(25, 30)
    # pstart = bit(30)
    # pend = bit(31)
