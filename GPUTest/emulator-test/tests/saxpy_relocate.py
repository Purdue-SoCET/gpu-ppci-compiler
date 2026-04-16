#!/usr/bin/env python3
"""
Rebuild saxpy *_data.hex and *_exp_*.hex from the CPU benchmark dumps.

The CPU reference prints host pointers in saxpyInput/Output.txt; those are meaningless
for the GPU emulator. This script parses only the *word values* (second column) in
dump order and lays them at a fixed GPU map:

  struct saxpy_arg_t @ 0x20000000  (16 bytes: n, a, x*, y*)
  x[0..n-1]      @ 0x20000010
  y[0..n-1]      @ 0x20000010 + 4*n

Run automatically after `datacopy` when ../benchmark/build/saxpyInput.txt exists.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

LINE_RE = re.compile(r"^\s*(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s*$")
DATA_START = 0x20000000
STRUCT_SIZE = 16  # int n, float a, float* x, float* y


def fbits(x: float) -> int:
    return struct.unpack("I", struct.pack("f", float(x)))[0]


def parse_words(path: Path) -> list[int]:
    words: list[int] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        m = LINE_RE.match(raw.strip())
        if not m:
            continue
        words.append(int(m.group(2), 16))
    return words


def repair_input_xy(n: int, xs: list[int], ys: list[int]) -> tuple[list[int], list[int]]:
    """Input: old saxpy_main used float as uint32 — x often dumps as 0,1,2,…"""
    if n > 0 and all(i < n and xs[i] == i for i in range(n)):
        return [fbits(float(i)) for i in range(n)], [fbits(float(2 * i)) for i in range(n)]
    return xs, ys


def repair_output_xy(n: int, xs: list[int], ys: list[int]) -> tuple[list[int], list[int]]:
    """Output: same broken x dump; y should be 4*i as float (or IEEE from memcpy)."""
    if n > 0 and all(i < n and xs[i] == i for i in range(n)):
        xs2 = [fbits(float(i)) for i in range(n)]
        if all(i < n and ys[i] == 4 * i for i in range(n)):
            ys2 = [fbits(float(4 * i)) for i in range(n)]
        else:
            ys2 = ys
        return xs2, ys2
    if n > 0 and all(i < n and ys[i] == 4 * i for i in range(n)):
        return xs, [fbits(float(4 * i)) for i in range(n)]
    return xs, ys


def layout(n: int, a_bits: int, xs: list[int], ys: list[int]) -> list[tuple[int, int]]:
    struct_base = DATA_START
    x_base = struct_base + STRUCT_SIZE
    y_base = x_base + 4 * n
    rows: list[tuple[int, int]] = [
        (struct_base, n & 0xFFFFFFFF),
        (struct_base + 4, a_bits & 0xFFFFFFFF),
        (struct_base + 8, x_base & 0xFFFFFFFF),
        (struct_base + 12, y_base & 0xFFFFFFFF),
    ]
    for i in range(n):
        rows.append((x_base + 4 * i, xs[i] & 0xFFFFFFFF))
        rows.append((y_base + 4 * i, ys[i] & 0xFFFFFFFF))
    rows.sort(key=lambda t: t[0])
    return rows


def write_hex(path: Path, rows: list[tuple[int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for addr, val in rows:
            f.write(f"0x{addr:08X} \t 0x{val:08X}\n")


def split_payload(words: list[int], label: str) -> tuple[int, int, list[int], list[int]]:
    if len(words) < 4 + 2:
        raise SystemExit(f"saxpy_relocate: {label}: too few words ({len(words)})")
    n = words[0]
    if n <= 0 or n > 4096:
        raise SystemExit(f"saxpy_relocate: {label}: bad n={n}")
    need = 4 + 2 * n
    if len(words) < need:
        raise SystemExit(f"saxpy_relocate: {label}: need {need} words, got {len(words)}")
    a_bits = words[1]
    # File order: x[0], y[0], x[1], y[1], … (not a contiguous x[] block)
    xs = [words[4 + 2 * i] for i in range(n)]
    ys = [words[4 + 2 * i + 1] for i in range(n)]
    return n, a_bits, xs, ys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--exp-suffix",
        default="t32_b1",
        help="Writes saxpy_exp_<suffix>.hex (default matches make test-saxpy defaults)",
    )
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    emu = here.parent
    bench_build = emu.parent / "benchmark" / "build"
    inp = bench_build / "saxpyInput.txt"
    outp = bench_build / "saxpyOutput.txt"
    out_dir = emu / "tests" / "complex_tests" / "saxpy"

    if not inp.is_file():
        return 0
    if not outp.is_file():
        print("saxpy_relocate: missing saxpyOutput.txt — run `make data-saxpy` first", file=sys.stderr)
        return 1

    w_in = parse_words(inp)
    w_out = parse_words(outp)

    n, a_in, x_in, y_in = split_payload(w_in, "saxpyInput.txt")
    n2, a_out, x_out, y_out = split_payload(w_out, "saxpyOutput.txt")
    if n != n2 or a_in != a_out:
        print("saxpy_relocate: Input/Output header mismatch", file=sys.stderr)
        return 1

    x_in, y_in = repair_input_xy(n, x_in, y_in)
    x_out, y_out = repair_output_xy(n, x_out, y_out)

    # CPU leaves x unchanged — if both parses agree on x bits after repair, use x_in for exp
    if x_in != x_out:
        print("saxpy_relocate: warning: Input vs Output x[] differ after repair; using Input x in exp", file=sys.stderr)

    write_hex(out_dir / "saxpy_data.hex", layout(n, a_in, x_in, y_in))
    write_hex(out_dir / f"saxpy_exp_{args.exp_suffix}.hex", layout(n, a_out, x_in, y_out))
    print(f"saxpy_relocate: wrote {out_dir / 'saxpy_data.hex'} and saxpy_exp_{args.exp_suffix}.hex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
