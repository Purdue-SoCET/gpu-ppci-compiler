#!/usr/bin/env python3
"""
Create a grouped bar chart of dynamic instruction counts across optimization levels.

Two input modes:
  1) CSV: --csv path/to/data.csv   (columns: instr,o0,o1,o2)
  2) Interactive: run without --csv and paste lines:
         ADDI 512 128 64
         LW   90  40  22
     Finish with an empty line.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


Row = Tuple[str, int, int, int]  # (instr, O0, O1, O2)


def _parse_int(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("empty integer")
    return int(s, 0)


def read_rows_from_csv(path: Path) -> List[Row]:
    rows: List[Row] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        need = {"instr", "o0", "o1", "o2"}
        if not r.fieldnames or not need.issubset(set(x.strip().lower() for x in r.fieldnames)):
            raise ValueError(f"CSV must have header columns: instr,o0,o1,o2 (got {r.fieldnames})")
        # normalize keys
        keymap = {k.strip().lower(): k for k in r.fieldnames}
        for i, d in enumerate(r, start=2):
            try:
                instr = (d.get(keymap["instr"]) or "").strip()
                if not instr:
                    raise ValueError("missing instr")
                o0 = _parse_int(d.get(keymap["o0"]) or "")
                o1 = _parse_int(d.get(keymap["o1"]) or "")
                o2 = _parse_int(d.get(keymap["o2"]) or "")
            except Exception as e:
                raise ValueError(f"bad CSV row at line {i}: {e}") from e
            rows.append((instr, o0, o1, o2))
    return rows


def read_rows_interactive(stdin: Iterable[str]) -> List[Row]:
    print("Enter lines: <INSTR> <O0> <O1> <O2>   (example: ADDI 512 128 64)")
    print("Finish with an empty line.")
    rows: List[Row] = []
    for raw in stdin:
        line = raw.strip()
        if not line:
            break
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"expected 4 tokens, got {len(parts)}: {line!r}")
        instr = parts[0]
        o0, o1, o2 = (_parse_int(parts[1]), _parse_int(parts[2]), _parse_int(parts[3]))
        rows.append((instr, o0, o1, o2))
    return rows


def plot(rows: List[Row], out: Path, title: str) -> None:
    try:
        import numpy as np
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("graph.py requires numpy + matplotlib") from e

    if not rows:
        raise ValueError("no rows provided")

    instrs = [r[0] for r in rows]
    o0 = np.array([r[1] for r in rows], dtype=np.int64)
    o1 = np.array([r[2] for r in rows], dtype=np.int64)
    o2 = np.array([r[3] for r in rows], dtype=np.int64)

    x = np.arange(len(instrs))
    w = 0.26

    fig, ax = plt.subplots(1, 1, figsize=(max(10, len(instrs) * 0.55), 5.8))
    ax.bar(x - w, o0, width=w, label="O0", color="#4C78A8", edgecolor="black", linewidth=0.3)
    ax.bar(x, o1, width=w, label="O1", color="#F58518", edgecolor="black", linewidth=0.3)
    ax.bar(x + w, o2, width=w, label="O2", color="#54A24B", edgecolor="black", linewidth=0.3)

    ax.set_title(title)
    ax.set_ylabel("Dynamic count")
    ax.set_xticks(x)
    ax.set_xticklabels(instrs, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()

    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=None, help="CSV file with columns: instr,o0,o1,o2")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("build/dyn_instr_Olevels.png"),
        help="Output PNG/SVG path",
    )
    ap.add_argument("--title", type=str, default="Dynamic instruction counts by optimization level")
    args = ap.parse_args(argv)

    if args.csv is not None:
        rows = read_rows_from_csv(args.csv)
    else:
        rows = read_rows_interactive(sys.stdin)
    plot(rows, args.out, args.title)
    print(f"Wrote {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

