"""Compile all kernels and generate disassembly output."""

import argparse
import os
import subprocess
import sys

KERNELS_DIR = "kernels"
BINARIES_DIR = "compiled_binaries"
DISASM_DIR = os.path.join(BINARIES_DIR, "disassembly")


def main():
    parser = argparse.ArgumentParser(
        description="Compile kernels and generate disassembly."
    )
    parser.add_argument(
        "-O2",
        dest="opt_o2",
        action="store_true",
        help="Compile with -O2 and append O2 to output filenames",
    )
    args = parser.parse_args()

    os.makedirs(BINARIES_DIR, exist_ok=True)
    os.makedirs(DISASM_DIR, exist_ok=True)

    sources = sorted(f for f in os.listdir(KERNELS_DIR) if f.endswith(".c"))

    if not sources:
        print("No .c files found in kernels/")
        sys.exit(1)

    failed = []

    for src in sources:
        name = os.path.splitext(src)[0]
        base_name = f"{name}O2" if args.opt_o2 else name
        src_path = os.path.join(KERNELS_DIR, src)
        hex_path = os.path.join(BINARIES_DIR, f"{base_name}.bin")
        disasm_path = os.path.join(DISASM_DIR, f"{base_name}.txt")
        entry = f"kernel_{name}"

        # Compile
        opt = ["-O", "2"] if args.opt_o2 else []
        print(f"[compile] {src_path} --entry {entry} " + " ".join(opt))
        compile_cmd = [
            "twig",
            src_path,
            "--entry",
            entry,
            "--hex-output",
            hex_path,
        ] + opt
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr.strip()}")
            failed.append((name, "compile", result.stderr.strip()))
            continue
        print(f"  -> {hex_path}")

        # Disassemble
        print(f"[disasm]  {hex_path}")
        disasm_cmd = ["tool", "--disasm", hex_path]
        result = subprocess.run(disasm_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr.strip()}")
            failed.append((name, "disasm", result.stderr.strip()))
            continue
        with open(disasm_path, "w") as f:
            f.write(result.stdout)
        print(f"  -> {disasm_path}")

    print()
    if failed:
        print(f"{len(failed)} failure(s):")
        for name, stage, err in failed:
            print(f"  {name} ({stage}): {err}")
        sys.exit(1)
    else:
        print(f"All {len(sources)} kernels built successfully.")


if __name__ == "__main__":
    main()
