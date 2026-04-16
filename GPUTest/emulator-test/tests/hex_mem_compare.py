#!/usr/bin/env python3
"""
Compare emulator memory (generated) against a CPU/reference dump (expected).

Used when test_hex.sh runs with RELAX_FP_HEX=1. Other tests use diff -u.

The CPU shader_memdump outputs only struct + pointed buffers (a subset of memory).
The emulator dump includes stack, spills, and other implementation addresses.
We therefore compare **only addresses that appear in the expected file**; extra
addresses in the generated dump are ignored.

- Addresses < DATA_START (instruction / low mem): exact uint32 match.
- Otherwise: exact match if either word is a pointer into this image; else
  math.isclose on IEEE floats (CPU vs emu rounding).
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path

DATA_START = 0x20000000
REL_TOL = 1e-4
ABS_TOL = 1e-5


def u32_to_float(w: int) -> float:
    return struct.unpack("<f", struct.pack("<I", w & 0xFFFFFFFF))[0]


def load_mem(path: Path) -> dict[int, int]:
    d: dict[int, int] = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.split("//")[0].split("#")[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[0].startswith("0x"):
            continue
        addr = int(parts[0], 16)
        val = int(parts[1], 16)
        d[addr] = val
    return d


def data_words_equal(a: int, b: int, addr_keys: set[int]) -> bool:
    if a == b:
        return True
    # Pointers and indices stored as raw bits must match exactly.
    if a in addr_keys or b in addr_keys:
        return False
    fa, fb = u32_to_float(a), u32_to_float(b)
    if math.isfinite(fa) and math.isfinite(fb):
        return math.isclose(fa, fb, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    return False


def compare(gen: dict[int, int], exp: dict[int, int]) -> tuple[bool, list[str]]:
    # Union of keys so pointer-valued words resolve against both memories.
    addr_keys = set(gen.keys()) | set(exp.keys())
    mismatches: list[str] = []
    # Reference-directed: every expected address must match generated; gen-only lines ignored.
    for addr in sorted(exp.keys()):
        ve = exp[addr]
        vg = gen.get(addr)
        if vg is None:
            mismatches.append(f"missing in gen: 0x{addr:08x} exp=0x{ve:08x}")
            continue
        if addr < DATA_START:
            ok = vg == ve
        else:
            ok = data_words_equal(vg, ve, addr_keys)
        if not ok:
            mismatches.append(
                f"0x{addr:08x} gen=0x{vg:08x} exp=0x{ve:08x} "
                f"(float {u32_to_float(vg)!r} vs {u32_to_float(ve)!r})"
            )
    return (len(mismatches) == 0, mismatches)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("generated", type=Path, help="Emulator output hex")
    ap.add_argument("expected", type=Path, help="Expected combined hex")
    ap.add_argument(
        "-n",
        "--max-report",
        type=int,
        default=40,
        help="Max mismatch lines to print (default 40)",
    )
    args = ap.parse_args()

    gen = load_mem(args.generated)
    exp = load_mem(args.expected)
    ok, lines = compare(gen, exp)
    if ok:
        sys.exit(0)
    print("hex_mem_compare: mismatch", file=sys.stderr)
    for ln in lines[: args.max_report]:
        print(ln, file=sys.stderr)
    if len(lines) > args.max_report:
        print(f"... and {len(lines) - args.max_report} more", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
