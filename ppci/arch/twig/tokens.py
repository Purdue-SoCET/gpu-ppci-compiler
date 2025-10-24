from ..token import Token, bit, bit_concat, bit_range


class TwigToken(Token):
    class Info:
        size = 32

    opcode = bit_range(6,0)
    rd = bit_range(12,7)
    rs1 = bit_range(18,13)
    rs2 = bit_range(24,19)
    imm12 = bit_range(24,19)
    imm6 = bit_range(24,13)
    pred = bit_range(29,25)
    pstart = bit_range(30,30)
    pend = bit_range(31,31)
