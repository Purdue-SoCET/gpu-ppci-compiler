#!/usr/bin/env python3
"""Print emulator flags matching test_hex.sh: --arg-pointer and optional stack range."""
import argparse
import json
import sys
from pathlib import Path

DATA_START = 0x20000000


def first_data_addr(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.split("//")[0].split("#")[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 1 and parts[0].startswith("0x"):
            addr = int(parts[0], 16)
            if addr >= DATA_START:
                return addr
    return DATA_START


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("hex_path", type=Path)
    ap.add_argument("--stack-json", type=Path, default=None)
    args = ap.parse_args()

    if not args.hex_path.is_file():
        print(f"emu_run_flags: file not found: {args.hex_path.resolve()}", file=sys.stderr)
        sys.exit(1)

    addr = first_data_addr(args.hex_path)
    out = ["--arg-pointer", f"0x{addr:08X}"]
    sj = args.stack_json
    if sj is not None and sj.is_file():
        data = json.loads(sj.read_text(encoding="utf-8"))
        out.extend(
            [
                "--stack-base",
                str(data["base_stack"]),
                "--stack-size",
                str(data["per_thread_stack_size"]),
            ]
        )
    print(" ".join(out))


if __name__ == "__main__":
    main()
