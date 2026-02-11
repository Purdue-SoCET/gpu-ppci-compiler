#!/usr/bin/env python3
from __future__ import annotations
import argparse
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple, List

# --------------------------
# Memory
# --------------------------

class MemFault(Exception):
    pass

class Memory:
    """
    Flat byte-addressable memory with bounds checking.
    """
    def __init__(self, size: int, base: int = 0):
        self.base = base
        self.size = size
        self.buf = bytearray(size)

    def _idx(self, addr: int, n: int = 1) -> int:
        off = addr - self.base
        if off < 0 or off + n > self.size:
            raise MemFault(f"Memory access OOB: addr=0x{addr:x}, n={n}, mem=[0x{self.base:x}..0x{self.base+self.size-1:x}]")
        return off

    def load_blob(self, addr: int, data: bytes):
        i = self._idx(addr, len(data))
        self.buf[i:i+len(data)] = data

    def rb(self, addr: int) -> int:
        return self.buf[self._idx(addr, 1)]

    def wb(self, addr: int, val: int):
        self.buf[self._idx(addr, 1)] = val & 0xFF

    def rw16(self, addr: int, little: bool = True) -> int:
        b0 = self.rb(addr)
        b1 = self.rb(addr+1)
        return b0 | (b1 << 8) if little else (b1 | (b0 << 8))

    def ww16(self, addr: int, val: int, little: bool = True):
        val &= 0xFFFF
        if little:
            self.wb(addr, val & 0xFF)
            self.wb(addr+1, (val >> 8) & 0xFF)
        else:
            self.wb(addr, (val >> 8) & 0xFF)
            self.wb(addr+1, val & 0xFF)

    def rw32(self, addr: int, little: bool = True) -> int:
        bs = [self.rb(addr+i) for i in range(4)]
        if little:
            return bs[0] | (bs[1]<<8) | (bs[2]<<16) | (bs[3]<<24)
        else:
            return bs[3] | (bs[2]<<8) | (bs[1]<<16) | (bs[0]<<24)

    def ww32(self, addr: int, val: int, little: bool = True):
        val &= 0xFFFFFFFF
        if little:
            for i in range(4):
                self.wb(addr+i, (val >> (8*i)) & 0xFF)
        else:
            for i in range(4):
                self.wb(addr+i, (val >> (8*(3-i))) & 0xFF)

# --------------------------
# CPU State
# --------------------------

@dataclass
class Decoded:
    mnem: str
    size: int
    exec_fn: Callable[["CPU", "Memory", "Decoded"], None]
    # optional decoded fields
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0
    raw: int = 0

class Halt(Exception):
    pass

class CPU:
    """
    Minimal CPU core: registers + pc + flags (optional).
    """
    def __init__(self, nregs: int = 16):
        self.reg: List[int] = [0] * nregs
        self.pc: int = 0
        self.steps: int = 0
        self.halted: bool = False

    def dump(self) -> str:
        cols = []
        for i, v in enumerate(self.reg):
            cols.append(f"r{i:02d}=0x{v:08x}")
        return " ".join(cols) + f" pc=0x{self.pc:08x}"

# --------------------------
# ISA / Decoder (你要改這裡)
# --------------------------

def sign_extend(x: int, bits: int) -> int:
    mask = (1 << bits) - 1
    x &= mask
    sign = 1 << (bits - 1)
    return (x ^ sign) - sign

def decode_toy16(cpu: CPU, mem: Memory, little: bool) -> Decoded:
    """
    範例 toy ISA: 16-bit fixed-length instructions.
    你之後要換成 twig 的 encoding：可以改成讀 16/32-bit、變長、等等。

    encoding (toy):
      [15:12] opcode
      [11:8]  rd
      [7:4]   rs1
      [3:0]   rs2_or_imm4

    op:
      0x0: NOP
      0x1: ADD  rd, rs1, rs2
      0x2: ADDI rd, rs1, imm4(sx)
      0x3: LD   rd, [rs1 + imm4(sx)]   (byte)
      0x4: ST   rs2, [rs1 + imm4(sx)]  (byte)  (rd欄位當rs2用)
      0xF: HALT
    """
    raw = mem.rw16(cpu.pc, little=little)
    op  = (raw >> 12) & 0xF
    rd  = (raw >> 8) & 0xF
    rs1 = (raw >> 4) & 0xF
    x   = raw & 0xF
    imm4 = sign_extend(x, 4)

    def op_nop(cpu: CPU, mem: Memory, d: Decoded):  # noqa
        pass

    def op_add(cpu: CPU, mem: Memory, d: Decoded):
        cpu.reg[d.rd] = (cpu.reg[d.rs1] + cpu.reg[d.rs2]) & 0xFFFFFFFF

    def op_addi(cpu: CPU, mem: Memory, d: Decoded):
        cpu.reg[d.rd] = (cpu.reg[d.rs1] + d.imm) & 0xFFFFFFFF

    def op_ld(cpu: CPU, mem: Memory, d: Decoded):
        addr = (cpu.reg[d.rs1] + d.imm) & 0xFFFFFFFF
        cpu.reg[d.rd] = mem.rb(addr)

    def op_st(cpu: CPU, mem: Memory, d: Decoded):
        addr = (cpu.reg[d.rs1] + d.imm) & 0xFFFFFFFF
        mem.wb(addr, cpu.reg[d.rd])  # 注意：toy 用 rd 當作 rs2

    def op_halt(cpu: CPU, mem: Memory, d: Decoded):  # noqa
        raise Halt()

    if op == 0x0:
        return Decoded("NOP", 2, op_nop, raw=raw)
    if op == 0x1:
        return Decoded("ADD", 2, op_add, rd=rd, rs1=rs1, rs2=x, raw=raw)
    if op == 0x2:
        return Decoded("ADDI", 2, op_addi, rd=rd, rs1=rs1, imm=imm4, raw=raw)
    if op == 0x3:
        return Decoded("LD", 2, op_ld, rd=rd, rs1=rs1, imm=imm4, raw=raw)
    if op == 0x4:
        return Decoded("ST", 2, op_st, rd=rd, rs1=rs1, imm=imm4, raw=raw)
    if op == 0xF:
        return Decoded("HALT", 2, op_halt, raw=raw)

    return Decoded(f"ILL(op=0x{op:x})", 2, lambda c,m,d: (_ for _ in ()).throw(RuntimeError(f"Illegal instr 0x{raw:04x} at pc=0x{cpu.pc:x}")), raw=raw)

# --------------------------
# Emulator
# --------------------------

class Emulator:
    def __init__(
        self,
        mem_size: int,
        mem_base: int,
        entry: int,
        nregs: int = 16,
        little_endian: bool = True,
        decoder: Callable[[CPU, Memory, bool], Decoded] = decode_toy16,
    ):
        self.mem = Memory(mem_size, base=mem_base)
        self.cpu = CPU(nregs=nregs)
        self.cpu.pc = entry
        self.little = little_endian
        self.decode = decoder
        self.breakpoints: set[int] = set()
        self.trace: bool = False

    def load_bin(self, bin_path: str, load_addr: int):
        with open(bin_path, "rb") as f:
            data = f.read()
        self.mem.load_blob(load_addr, data)

    def step(self):
        if self.cpu.pc in self.breakpoints:
            raise Halt(f"Hit breakpoint at pc=0x{self.cpu.pc:x}")

        d = self.decode(self.cpu, self.mem, self.little)

        if self.trace:
            print(self.format_trace(d))

        old_pc = self.cpu.pc
        self.cpu.pc = (self.cpu.pc + d.size) & 0xFFFFFFFF  # default pc+len
        d.exec_fn(self.cpu, self.mem, d)

        self.cpu.steps += 1
        if self.cpu.pc == old_pc and d.mnem.startswith("ILL"):
            # safety
            raise RuntimeError("PC did not advance on illegal instruction")

    def run(self, max_steps: int = 1_000_000):
        try:
            for _ in range(max_steps):
                self.step()
        except Halt as e:
            if str(e):
                print(f"[HALT] {e}")
            else:
                print("[HALT]")
        except MemFault as e:
            print(f"[MEMFAULT] {e}")
            raise
        except Exception as e:
            print(f"[EXCEPTION] {e}")
            raise

    def format_trace(self, d: Decoded) -> str:
        # 你可以改成顯示更多欄位/flags/記憶體存取等
        fields = []
        if d.mnem in ("ADD","ADDI","LD","ST"):
            fields.append(f"rd=r{d.rd}")
            fields.append(f"rs1=r{d.rs1}")
        if d.mnem == "ADD":
            fields.append(f"rs2=r{d.rs2}")
        if d.mnem in ("ADDI","LD","ST"):
            fields.append(f"imm={d.imm}")
        fstr = " ".join(fields)
        return f"pc=0x{(self.cpu.pc):08x} raw=0x{d.raw:04x} {d.mnem} {fstr} | {self.cpu.dump()}"

# --------------------------
# CLI
# --------------------------

def parse_int(x: str) -> int:
    return int(x, 0)

def main():
    ap = argparse.ArgumentParser(description="prog.bin emulator skeleton (plug-in ISA decoder)")
    ap.add_argument("bin", help="prog.bin path")
    ap.add_argument("--mem-base", type=parse_int, default=0x00000000, help="memory base address")
    ap.add_argument("--mem-size", type=parse_int, default=0x00100000, help="memory size bytes")
    ap.add_argument("--load-addr", type=parse_int, default=0x00000000, help="where to load prog.bin")
    ap.add_argument("--entry", type=parse_int, default=0x00000000, help="entry PC")
    ap.add_argument("--regs", type=int, default=16, help="number of GPRs")
    ap.add_argument("--big", action="store_true", help="use big endian fetch (default little)")
    ap.add_argument("--trace", action="store_true", help="print instruction trace")
    ap.add_argument("--bp", action="append", default=[], help="breakpoint address (can repeat)")
    ap.add_argument("--max-steps", type=int, default=200000, help="max executed steps")
    args = ap.parse_args()

    emu = Emulator(
        mem_size=args.mem_size,
        mem_base=args.mem_base,
        entry=args.entry,
        nregs=args.regs,
        little_endian=(not args.big),
        decoder=decode_toy16,  # TODO: 換成你的 twig decoder
    )
    emu.trace = args.trace
    for b in args.bp:
        emu.breakpoints.add(parse_int(b))

    emu.load_bin(args.bin, args.load_addr)
    emu.run(max_steps=args.max_steps)

if __name__ == "__main__":
    main()