from ... import ir
from ..registers import Register, RegisterClass

# pylint: disable=invalid-name


class TwigRegister(Register):
    bitsize = 32

    @classmethod
    def from_num(cls, num):
        return num2regmap[num]

    @classmethod
    def all_registers(cls):
        return registers

    def __repr__(self):
        if self.is_colored:
            return get_register(self.color).name
            return f"{self.name}={self.color}"
        else:
            return self.name


class TwigProgramCounterRegister(Register):
    bitsize = 32

#maybe this should not even extend Register and should have it's own class
#TODO: add predicate logic after initial asm is generatable
#TODO: add packeting after
#TODO: add rfc after
class TwigPredRegister(Register):
    bitsize = 32
    @classmethod
    def from_num(cls, num):
        return num2predregmap[num]
    @classmethod
    def all_registers(cls):
        return predregisters


def get_register(n):
    """Based on a number, get the corresponding register"""
    return num2regmap[n]


def register_range(a, b):
    """Return set of registers from a to b"""
    assert a.num < b.num
    return {get_register(n) for n in range(a.num, b.num + 1)}


R0 = TwigRegister("x0", num=0, aka=("zero",))
LR = TwigRegister("x1", num=1, aka=("ra",))
SP = TwigRegister("x2", num=2, aka=("sp",))
R3 = TwigRegister("x3", num=3, aka=("gp",))
R4 = TwigRegister("x4", num=4, aka=("tp",))
R5 = TwigRegister("x5", num=5, aka=("t0",))
R6 = TwigRegister("x6", num=6, aka=("t1",))
R7 = TwigRegister("x7", num=7, aka=("t2",))
FP = TwigRegister("x8", num=8, aka=("s0", "fp"))
R9 = TwigRegister("x9", num=9, aka=("s1",))
R10 = TwigRegister("x10", num=10, aka=("a0",))
R11 = TwigRegister("x11", num=11, aka=("a1",))
R12 = TwigRegister("x12", num=12, aka=("a2",))
R13 = TwigRegister("x13", num=13, aka=("a3",))
R14 = TwigRegister("x14", num=14, aka=("a4",))
R15 = TwigRegister("x15", num=15, aka=("a5",))
R16 = TwigRegister("x16", num=16, aka=("a6",))
R17 = TwigRegister("x17", num=17, aka=("a7",))
R18 = TwigRegister("x18", num=18, aka=("s2",))
R19 = TwigRegister("x19", num=19, aka=("s3",))
R20 = TwigRegister("x20", num=20, aka=("s4",))
R21 = TwigRegister("x21", num=21, aka=("s5",))
R22 = TwigRegister("x22", num=22, aka=("s6",))
R23 = TwigRegister("x23", num=23, aka=("s7",))
R24 = TwigRegister("x24", num=24, aka=("s8",))
R25 = TwigRegister("x25", num=25, aka=("s9",))
R26 = TwigRegister("x26", num=26, aka=("s10",))
R27 = TwigRegister("x27", num=27, aka=("s11",))
R28 = TwigRegister("x28", num=28, aka=("t3",))
R29 = TwigRegister("x29", num=29, aka=("t4",))
R30 = TwigRegister("x30", num=30, aka=("t5",))
R31 = TwigRegister("x31", num=31, aka=("t6",))
R32 = TwigRegister("x32", num=32, aka=("s12",))
R33 = TwigRegister("x33", num=33, aka=("s13",))
R34 = TwigRegister("x34", num=34, aka=("s14",))
R35 = TwigRegister("x35", num=35, aka=("s15",))
R36 = TwigRegister("x36", num=36, aka=("s16",))
R37 = TwigRegister("x37", num=37, aka=("s17",))
R38 = TwigRegister("x38", num=38, aka=("s18",))
R39 = TwigRegister("x39", num=39, aka=("s19",))
R40 = TwigRegister("x40", num=40, aka=("s20",))
R41 = TwigRegister("x41", num=41, aka=("s21",))
R42 = TwigRegister("x42", num=42, aka=("s22",))
R43 = TwigRegister("x43", num=43, aka=("s23",))
R44 = TwigRegister("x44", num=44, aka=("s24",))
R45 = TwigRegister("x45", num=45, aka=("s25",))
R46 = TwigRegister("x46", num=46, aka=("s26",))
R47 = TwigRegister("x47", num=47, aka=("s27",))
R48 = TwigRegister("x48", num=48, aka=("s28",))
R49 = TwigRegister("x49", num=49, aka=("s29",))
R50 = TwigRegister("x50", num=50, aka=("s30",))
R51 = TwigRegister("x51", num=51, aka=("s31",))
R52 = TwigRegister("x52", num=52, aka=("s32",))
R53 = TwigRegister("x53", num=53, aka=("s33",))
R54 = TwigRegister("x54", num=54, aka=("s34",))
R55 = TwigRegister("x55", num=55, aka=("s35",))
R56 = TwigRegister("x56", num=56, aka=("s36",))
R57 = TwigRegister("x57", num=57, aka=("s37",))
R58 = TwigRegister("x58", num=58, aka=("s38",))
R59 = TwigRegister("x59", num=59, aka=("s39",))
R60 = TwigRegister("x60", num=60, aka=("s40",))
R61 = TwigRegister("x61", num=61, aka=("s41",))
R62 = TwigRegister("x62", num=62, aka=("s42",))
R63 = TwigRegister("x63", num=63, aka=("s43",))


PC = TwigProgramCounterRegister("PC", num=64)

P0 = TwigPredRegister("p0", num=65, aka=("p0",))
P1 = TwigPredRegister("p1", num=66, aka=("p1",))
P2 = TwigPredRegister("p2", num=67, aka=("p2",))
P3 = TwigPredRegister("p3", num=68, aka=("p3",))
P4 = TwigPredRegister("p4", num=69, aka=("p4",))
P5 = TwigPredRegister("p5", num=70, aka=("p5",))
P6 = TwigPredRegister("p6", num=71, aka=("p6",))
P7 = TwigPredRegister("p7", num=72, aka=("p7",))
P8 = TwigPredRegister("p8", num=73, aka=("p8",))
P9 = TwigPredRegister("p9", num=74, aka=("p9",))
P10 = TwigPredRegister("p10", num=75, aka=("p10",))
P11 = TwigPredRegister("p11", num=76, aka=("p11",))
P12 = TwigPredRegister("p12", num=77, aka=("p12",))
P13 = TwigPredRegister("p13", num=78, aka=("p13",))
P14 = TwigPredRegister("p14", num=79, aka=("p14",))
P15 = TwigPredRegister("p15", num=80, aka=("p15",))
P16 = TwigPredRegister("p16", num=81, aka=("p16",))
P17 = TwigPredRegister("p17", num=82, aka=("p17",))
P18 = TwigPredRegister("p18", num=83, aka=("p18",))
P19 = TwigPredRegister("p19", num=84, aka=("p19",))
P20 = TwigPredRegister("p20", num=85, aka=("p20",))
P21 = TwigPredRegister("p21", num=86, aka=("p21",))
P22 = TwigPredRegister("p22", num=87, aka=("p22",))
P23 = TwigPredRegister("p23", num=88, aka=("p23",))
P24 = TwigPredRegister("p24", num=89, aka=("p24",))
P25 = TwigPredRegister("p25", num=90, aka=("p25",))
P26 = TwigPredRegister("p26", num=91, aka=("p26",))
P27 = TwigPredRegister("p27", num=92, aka=("p27",))
P28 = TwigPredRegister("p28", num=93, aka=("p28",))
P29 = TwigPredRegister("p29", num=94, aka=("p29",))
P30 = TwigPredRegister("p30", num=95, aka=("p30",))
P31 = TwigPredRegister("p31", num=96, aka=("p31",))


registers = [
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
    R63
]
TwigRegister.registers = registers

predregisters = [
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
    P31
]


TwigPredRegister.predregisters = predregisters
num2regmap = {r.num: r for r in registers}
num2predregmap = {p.num: p for p in predregisters}

gdb_registers = registers + [PC] + predregisters

# register_classes_hwfp = [
#     RegisterClass(
#         "reg",
#         [ir.i8, ir.i16, ir.i32, ir.ptr, ir.u8, ir.u16, ir.u32],
#         TwigRegister,
#         [
#             R9,
#             R10,
#             R11,
#             R12,
#             R13,
#             R14,
#             R15,
#             R16,
#             R17,
#             R18,
#             R19,
#             R20,
#             R21,
#             R22,
#             R23,
#             R24,
#             R25,
#             R26,
#             R27,
#         ],
#     ),
#     RegisterClass("freg", [ir.f32, ir.f64], TwigFRegister, fregisters),
# ]

register_classes_swfp = [
    RegisterClass(
        "reg",
        [ir.i8, ir.i16, ir.i32, ir.ptr, ir.u8, ir.u16, ir.u32, ir.f32, ir.f64],
        TwigRegister,
        [
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
            P31
        ],
    )
]
