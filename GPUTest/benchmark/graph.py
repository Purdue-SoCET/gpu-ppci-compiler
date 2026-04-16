#!/usr/bin/env python3
"""
Create a grouped bar chart of dynamic instruction counts across optimization levels.

Two input modes:
  1) CSV: --csv path/to/<kernel>.csv   (columns: instr,o0,o1,o2)
     Default output: <kernel>_dyn_cnt.png in the current working directory.
  2) Interactive: run without --csv and paste lines:
         ADDI 512 128 64
         LW   90  40  22
     Finish with an empty line. Default output: dyn_cnt.png
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# to be edited before generating the figure
RUNTIME_O0_SEC = 5.00000  # (default)
RUNTIME_O1_SEC = 4.00000
RUNTIME_O2_SEC = 3.00000

# Bar / legend colors (match)
COLOR_O0 = "#4C78A8"
COLOR_O1 = "#F58518"
COLOR_O2 = "#54A24B"

LEGEND_FONTSIZE = 12

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


def _chart_title(kernel_from_csv: Optional[str]) -> str:
    base = "dynamic instruction count by optimization level"
    if kernel_from_csv:
        return f"{base} KERNEL = {kernel_from_csv}"
    return base


def plot(rows: List[Row], out: Path, title: str) -> None:
    try:
        import numpy as np
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch
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
    ax.bar(x - w, o0, width=w, label="O0", color=COLOR_O0, edgecolor="black", linewidth=0.3)
    ax.bar(x, o1, width=w, label="O1", color=COLOR_O1, edgecolor="black", linewidth=0.3)
    ax.bar(x + w, o2, width=w, label="O2", color=COLOR_O2, edgecolor="black", linewidth=0.3)

    ax.set_title(title, fontsize=12)
    ax.set_ylabel("Count")
    ax.set_xticks(x)
    ax.set_xticklabels(instrs, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.25)

    legend_handles = [
        Patch(
            facecolor=COLOR_O0,
            edgecolor="black",
            linewidth=0.3,
            label=f"O=0, runtime = {RUNTIME_O0_SEC:.5f} (default) sec",
        ),
        Patch(
            facecolor=COLOR_O1,
            edgecolor="black",
            linewidth=0.3,
            label=f"O=1, runtime = {RUNTIME_O1_SEC:.5f} sec",
        ),
        Patch(
            facecolor=COLOR_O2,
            edgecolor="black",
            linewidth=0.3,
            label=f"O=2, runtime = {RUNTIME_O2_SEC:.5f} sec",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper right",
        fontsize=LEGEND_FONTSIZE,
        frameon=True,
        fancybox=False,
        edgecolor="0.6",
    )

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
        default=None,
        help="Output PNG/SVG path (default: <kernel>_dyn_cnt.png next to CSV, or dyn_cnt.png)",
    )
    ap.add_argument(
        "--title",
        type=str,
        default=None,
        help="Override chart title (default: built from CSV kernel name if any)",
    )
    args = ap.parse_args(argv)

    kernel_from_csv: Optional[str] = None
    if args.csv is not None:
        rows = read_rows_from_csv(args.csv)
        kernel_from_csv = args.csv.stem
    else:
        rows = read_rows_interactive(sys.stdin)

    title = args.title if args.title is not None else _chart_title(kernel_from_csv)

    if args.out is not None:
        out = args.out
    elif args.csv is not None:
        out = Path(f"{kernel_from_csv}_dyn_cnt.png")
    else:
        out = Path("dyn_cnt.png")

    plot(rows, out, title)
    print(f"Wrote {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
