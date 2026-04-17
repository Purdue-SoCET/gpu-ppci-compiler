#!/bin/bash

# ==========================================
# test_hex.sh - Run emulator tests with .hex input directly (no assembler)
# Windows Git Bash compatible - uses python instead of make
# ==========================================

# ==========================================
# Configuration
# ==========================================
TEST_ROOT="tests"
DIFF_DIR="test_diffs"
EMULATOR="cardinal-ISS/src/emulator.py"
DATA_START=0x00100000  # Address threshold: below = instructions, above = data

# Intermediate files (we never delete the user's input .hex)
MEMINIT="meminit.hex"                 # Working copy for emulator (may be temp)
MEMINIT_PATCHED="meminit_patched.hex" # Per-run copy with MMIO values injected
EMU_OUTPUT="memsim.hex"
FINAL_EXPECTED="final_expected_combined.hex"
TEMP_CMD_LOG="temp_command_output.txt"
INSTR_PART="temp_instr_part.hex"       # Instruction section for comparison

# Python: prefer python3, fallback to python (Windows)
PYTHON=""
for p in python3 python; do
    if command -v "$p" &>/dev/null; then
        PYTHON="$p"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Error: Neither python3 nor python found."
    exit 1
fi

# Counters
PASS_COUNT=0
FAIL_COUNT=0
MISSING_COUNT=0

# Stack range (read from sidecar .stack.json if present)
STACK_BASE=""
STACK_SIZE=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==========================================
# Get first data-region address from hex file (addr >= DATA_START)
# Used as default argptr when -a not specified.
# ==========================================
get_first_data_addr() {
    local file="$1"
    "$PYTHON" -c "
import sys
data_start = 0x00100000
with open(sys.argv[1]) as f:
    for line in f:
        line = line.split('//')[0].split('#')[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 1 and parts[0].startswith('0x'):
            addr = int(parts[0], 16)
            if addr >= data_start:
                print(f'0x{addr:08X}')
                sys.exit(0)
print('0x00100000')
" "$file"
}

# ==========================================
# Sort hex file by address (ascending) for stable diff comparison.
# Also deduplicates by address (last value for each address wins) and
# normalises to lowercase address + lowercase data with a single space,
# so that diff -w -i never trips over whitespace/case duplicates.
# Format: 0xADDR 0xDATA per line
# ==========================================
sort_hex_by_addr() {
    local file="$1"
    [ ! -f "$file" ] && return 0
    "$PYTHON" -c "
import sys
import re
path = sys.argv[1]
pattern = re.compile(r'^\s*(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s*')
seen = {}   # addr -> canonical line (last value wins, so exp beats instr)
with open(path) as f:
    for line in f:
        line = line.rstrip('\n\r')
        m = pattern.match(line.split('//')[0].split('#')[0].strip())
        if m:
            addr = int(m.group(1), 16)
            data = int(m.group(2), 16)
            seen[addr] = (addr, f'0x{addr:08x} 0x{data:08x}')
with open(path, 'w') as f:
    for _, ln in sorted(seen.values(), key=lambda x: x[0]):
        f.write(ln + '\n')
" "$file"
}

# ==========================================
# Inject MMIO register values into a patched copy of MEMINIT.
# MMIO words are written first so they appear at the top of the file:
#   0x0000000C = 0x00000024  (entry point, fixed)
#   0x00000010 = threads     (threads per block)
#   0x00000018 = 1024*blocks (total_threads per block-group)
#   0x0000001C = argptr      (argument pointer)
# Usage: inject_mmio_patched <src_hex> <threads> <blocks> <argptr_hex>
# ==========================================
inject_mmio_patched() {
    local src="$1" threads="$2" blocks="$3" argptr_hex="$4"
    "$PYTHON" -c "
import sys
src = sys.argv[1]
threads = int(sys.argv[2])
blocks  = int(sys.argv[3])
argptr  = int(sys.argv[4], 16)
total_threads = 1024 * blocks
with open(src) as f:
    content = f.read()
with open('$MEMINIT_PATCHED', 'w') as f:
    f.write(f'0x{0x0C:08x} 0x{0x00000024:08x}\n')
    f.write(f'0x{0x10:08x} 0x{threads:08x}\n')
    f.write(f'0x{0x18:08x} 0x{total_threads:08x}\n')
    f.write(f'0x{0x1C:08x} 0x{argptr:08x}\n')
    f.write(content)
" "$src" "$threads" "$blocks" "$argptr_hex"
}

# ==========================================
# Save dry-run outputs: meminit_patched → test_diffs/<id>_meminit.hex
#                       instr + expected  → test_diffs/<id>_memsim.hex
# Usage: save_dry_run_output <dest_id> [exp_file]
# ==========================================
save_dry_run_output() {
    local dest_id="$1"
    local exp_file="${2:-}"
    local meminit_out="$DIFF_DIR/${dest_id}_meminit.hex"
    local memsim_out="$DIFF_DIR/${dest_id}_memsim.hex"

    # Meminit: copy patched file (MMIO already at top) and sort so addresses are ordered
    cp "$MEMINIT_PATCHED" "$meminit_out"
    sort_hex_by_addr "$meminit_out"

    # memsim: grep the full instruction+MMIO region from the patched meminit
    # (addresses 0x0xxxxxxx and 0x1xxxxxxx, which includes MMIO at 0x0C/0x10/0x18/0x1C
    # and code at 0x24+), then append expected data if present, then sort.
    grep -E '^0x[01][0-9a-fA-F]{7}[[:space:]]' "$MEMINIT_PATCHED" > "$memsim_out" 2>/dev/null || true
    if [ -n "$exp_file" ] && [ -f "$exp_file" ]; then
        cat "$exp_file" >> "$memsim_out"
    fi
    sort_hex_by_addr "$memsim_out"

    echo -e "${BLUE}[DRY RUN]${NC}  $dest_id"
    echo "           meminit:   $meminit_out"
    echo "           memsim: $memsim_out"
}

# Compare EMU_OUTPUT to FINAL_EXPECTED; pass --allow-approx to diffs.py when ALLOW_APPROX=1.
compare_hex_against_expected() {
    local error_log="$1"
    local cmp_args=("$PYTHON" "$SCRIPT_DIR/tests/diffs.py" --compare)
    if [ "$ALLOW_APPROX" = "1" ]; then
        cmp_args+=(--allow-approx)
    fi
    cmp_args+=("$EMU_OUTPUT" "$FINAL_EXPECTED" "$error_log")
    "${cmp_args[@]}"
}

# ==========================================
# Run emulator (replaces: make run INPUT=... THREADS=... BLOCKS=...)
# ==========================================
run_emulator() {
    local input_path="$1"
    local threads="$2"
    local blocks="$3"
    local extra_args=()
    # When -l is not specified, do not pass --log-thread so the emulator prints trace for all threads.
    # When -l TID is specified, pass --log-thread to restrict trace to that thread only.
    [ -n "$LOG_THREAD" ] && extra_args+=(--log-thread "$LOG_THREAD")
    [ -n "$STACK_BASE" ]  && extra_args+=(--stack-base "$STACK_BASE")
    [ -n "$STACK_SIZE" ]  && extra_args+=(--stack-size "$STACK_SIZE")
    inject_mmio_patched "$input_path" "$threads" "$blocks" "$ARGPTR"
    if [ "$DRY_RUN" = "1" ]; then
        return 0
    fi
    "$PYTHON" "$EMULATOR" -t "$threads" -b "$blocks" --start-pc 0x24 --mem-format hex --arg-pointer "$ARGPTR" "${extra_args[@]}" "$MEMINIT_PATCHED"
}

# Run emulator and capture output to TEMP_CMD_LOG (trace file). Never prints to terminal.
# Sets EMULATOR_EXIT for the caller to check.
run_emulator_capture() {
    run_emulator "$@" > "$TEMP_CMD_LOG" 2>&1
    EMULATOR_EXIT=$?
}

# ==========================================
# Setup - change to script directory (Windows-friendly)
# ==========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# ==========================================
# Parse arguments: -t/--threads (1-1024), -b/--blocks (1-1024), -a/--argptr, -l/--log-thread, --allow-approx
# ==========================================
THREADS_OVERRIDE=""
BLOCKS_OVERRIDE=""
ARGPTR=""  # default: first data-region addr in input file
LOG_THREAD=""
# 0 = strict uint32 compare; 1 = allow float ULP slack in data region (see tests/diffs.py)
ALLOW_APPROX=0
# 1 = build and print the patched meminit then exit without running the emulator
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--threads)
            THREADS_OVERRIDE="$2"
            shift 2
            ;;
        -b|--blocks)
            BLOCKS_OVERRIDE="$2"
            shift 2
            ;;
        -a|--argptr)
            ARGPTR="$2"
            shift 2
            ;;
        -l|--log-thread)
            LOG_THREAD="$2"
            shift 2
            ;;
        --allow-approx)
            ALLOW_APPROX=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options] <path/to/file.hex>"
            echo "  -t, --threads N    Number of threads per block (1-1024)"
            echo "  -b, --blocks N     Number of blocks (1-1024)"
            echo "  -a, --argptr ADDR  Argument pointer address (default: first data addr in input)"
            echo "  -l, --log-thread TID  Only log trace for this global thread id (blockIdx*blockDim+threadIdx). Omit to log all threads."
            echo "  --allow-approx     Allow float32 ULP tolerance (<=12) for data addresses >= 0x00100000"
            echo "  --dry-run          Build patched meminit + memsim (instr+expected) in test_diffs/; skip emulator"
            exit 0
            ;;
        *)
            HEX_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "${HEX_FILE:-}" ]; then
    echo -e "${RED}Error:${NC} Usage: $0 [options] <path/to/file.hex>"
    exit 1
fi

# Validate threads override if provided
if [ -n "$THREADS_OVERRIDE" ]; then
    if ! [[ "$THREADS_OVERRIDE" =~ ^[0-9]+$ ]] || [ "$THREADS_OVERRIDE" -lt 1 ] || [ "$THREADS_OVERRIDE" -gt 1024 ]; then
        echo -e "${RED}Error:${NC} Threads must be between 1 and 1024 (got: $THREADS_OVERRIDE)"
        exit 1
    fi
fi

# Validate blocks override if provided
if [ -n "$BLOCKS_OVERRIDE" ]; then
    if ! [[ "$BLOCKS_OVERRIDE" =~ ^[0-9]+$ ]] || [ "$BLOCKS_OVERRIDE" -lt 1 ] || [ "$BLOCKS_OVERRIDE" -gt 1024 ]; then
        echo -e "${RED}Error:${NC} Blocks must be between 1 and 1024 (got: $BLOCKS_OVERRIDE)"
        exit 1
    fi
fi

# Paths are relative to emulator dir (we cd'd to script dir above)

if [ ! -f "$HEX_FILE" ]; then
    echo -e "${RED}Error:${NC} File not found: $HEX_FILE"
    exit 1
fi

# Derive base name and directory for expected files
dir_name=$(dirname "$HEX_FILE")
base_name=$(basename "$HEX_FILE" .hex)

mkdir -p "$DIFF_DIR"
rm -f "$MEMINIT" "$MEMINIT_PATCHED" "$EMU_OUTPUT" "$FINAL_EXPECTED" "$TEMP_CMD_LOG" "$INSTR_PART"
# Note: we never delete the user's input file

# ==========================================
# 1. Prepare MEMINIT
# ==========================================
# Check if file is pre-formatted (0xADDR 0xDATA) or raw (single hex per line)
first_line=$(head -n 1 "$HEX_FILE" | tr -d '\r')
part_count=$(echo "$first_line" | awk '{print NF}')

if [ "$part_count" -eq 2 ]; then
    # Pre-formatted: use as MEMINIT directly (copy, don't modify original)
    cp "$HEX_FILE" "$MEMINIT"
else
    # Raw format: add addresses like assembler output
    awk '{v=$0; gsub(/^0x/,"",v); printf "0x%08x 0x%s\n", 0x24 + (NR-1)*4, v}' "$HEX_FILE" > "$MEMINIT"
    # Optionally append _data.hex if present
    input_data_file=$(find "$dir_name" -maxdepth 1 -name "${base_name}_data.hex" 2>/dev/null | head -n 1)
    if [ -n "$input_data_file" ]; then
        cat "$input_data_file" >> "$MEMINIT"
    fi
fi

# Use MEMINIT for emulator (we created it from user's file)
INPUT_TO_USE="$MEMINIT"

# Set default argptr from first data address if not overridden by -a
if [ -z "$ARGPTR" ]; then
    ARGPTR=$(get_first_data_addr "$INPUT_TO_USE")
fi

# Read stack info sidecar (<basename>.stack.json) if present
stack_json="${dir_name}/${base_name}.stack.json"
if [ -f "$stack_json" ]; then
    read STACK_BASE STACK_SIZE < <("$PYTHON" -c "
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
print(d.get('base_stack', ''), d.get('per_thread_stack_size', ''))
" "$stack_json")
fi

echo "========================================"
echo "      GPU Emulator - Hex Input Test"
echo "      Input:   $HEX_FILE"
echo "      Base:    $base_name"
echo "      Argptr:  $ARGPTR"
if [ "$ALLOW_APPROX" = "1" ]; then
    echo "      ULP:     allow (data region float tolerance)"
else
    echo "      ULP:     strict (exact words)"
fi
echo "========================================"

# ==========================================
# 2. INSTR_PART is extracted per-run from MEMINIT_PATCHED (after inject_mmio_patched),
#    so the MMIO values at 0x0C/0x10/0x18/0x1C are included in the comparison baseline.
#    Initialise to empty here; each test run overwrites it.
# ==========================================
touch "$INSTR_PART"

# ==========================================
# 3. Find expected files and run tests
# ==========================================
expected_files=$(find "$dir_name" -maxdepth 1 -name "${base_name}_exp_*.hex" 2>/dev/null | sort)

# If threads or blocks override is set, use it and run single config (compare only if matching expected exists)
if [ -n "$THREADS_OVERRIDE" ] || [ -n "$BLOCKS_OVERRIDE" ]; then
    THREADS="${THREADS_OVERRIDE:-32}"
    BLOCKS="${BLOCKS_OVERRIDE:-1}"
    exp_file=$(find "$dir_name" -maxdepth 1 -name "${base_name}_exp_t${THREADS}_b${BLOCKS}.hex" 2>/dev/null | head -n 1)

    run_emulator_capture "$INPUT_TO_USE" "$THREADS" "$BLOCKS"
    grep -E '^0x000[0-9a-fA-F]{5}[[:space:]]' "$MEMINIT_PATCHED" > "$INSTR_PART" 2>/dev/null || true

    if [ "$DRY_RUN" = "1" ]; then
        save_dry_run_output "${base_name}_t${THREADS}_b${BLOCKS}" "$exp_file"
    elif [ "$EMULATOR_EXIT" -ne 0 ] || [ ! -f "$EMU_OUTPUT" ]; then
        echo -e "${RED}[RUN FAIL]${NC} $base_name (t=$THREADS, b=$BLOCKS)"
        mv "$TEMP_CMD_LOG" "$DIFF_DIR/${base_name}_run_error.log"
        cp "$MEMINIT_PATCHED" "$DIFF_DIR/${base_name}_meminit.hex"
        ((FAIL_COUNT++))
    elif [ -z "$exp_file" ]; then
        echo -e "${YELLOW}[NO REF]${NC}   $base_name (t=$THREADS, b=$BLOCKS) - Output saved"
        sort_hex_by_addr "$EMU_OUTPUT"
        cp "$EMU_OUTPUT" "$DIFF_DIR/${base_name}_gen.hex"
        cp "$MEMINIT_PATCHED" "$DIFF_DIR/${base_name}_meminit.hex"
        ((MISSING_COUNT++))
    else
        test_id="${base_name}_t${THREADS}_b${BLOCKS}"
        error_log="$DIFF_DIR/${test_id}_error.log"
        cat "$INSTR_PART" "$exp_file" > "$FINAL_EXPECTED"
        sort_hex_by_addr "$EMU_OUTPUT"
        sort_hex_by_addr "$FINAL_EXPECTED"
        compare_hex_against_expected "$error_log"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[PASS]${NC}     $base_name (t=$THREADS, b=$BLOCKS)"
            rm -f "$error_log"
            ((PASS_COUNT++))
        else
            echo -e "${RED}[FAIL]${NC}     $base_name (t=$THREADS, b=$BLOCKS)"
            cp "$EMU_OUTPUT" "$DIFF_DIR/${test_id}_gen.hex"
            cp "$FINAL_EXPECTED" "$DIFF_DIR/${test_id}_exp.hex"
            cp "$MEMINIT_PATCHED" "$DIFF_DIR/${test_id}_meminit.hex"
            cp "$TEMP_CMD_LOG" "$DIFF_DIR/${test_id}_trace.log"
            ((FAIL_COUNT++))
        fi
    fi
elif [ -z "$expected_files" ]; then
    # --- No expected files: run with default config ---
    THREADS=32
    BLOCKS="${BLOCKS_OVERRIDE:-1}"

    run_emulator_capture "$INPUT_TO_USE" "$THREADS" "$BLOCKS"
    grep -E '^0x000[0-9a-fA-F]{5}[[:space:]]' "$MEMINIT_PATCHED" > "$INSTR_PART" 2>/dev/null || true

    if [ "$DRY_RUN" = "1" ]; then
        save_dry_run_output "${base_name}_t${THREADS}_b${BLOCKS}"
    elif [ "$EMULATOR_EXIT" -ne 0 ] || [ ! -f "$EMU_OUTPUT" ]; then
        echo -e "${RED}[RUN FAIL]${NC} $base_name (t=$THREADS)"
        mv "$TEMP_CMD_LOG" "$DIFF_DIR/${base_name}_run_error.log"
        cp "$MEMINIT_PATCHED" "$DIFF_DIR/${base_name}_meminit.hex"
        ((FAIL_COUNT++))
    else
        echo -e "${YELLOW}[NO REF]${NC}   $base_name (t=$THREADS) - Output saved"
        sort_hex_by_addr "$EMU_OUTPUT"
        cp "$EMU_OUTPUT" "$DIFF_DIR/${base_name}_gen.hex"
        cp "$MEMINIT_PATCHED" "$DIFF_DIR/${base_name}_meminit.hex"
        ((MISSING_COUNT++))
    fi
else
    # --- Multiple configurations from expected files ---
    for exp_file in $expected_files; do
        THREADS=32
        BLOCKS=1
        if [[ "$exp_file" =~ _t([0-9]+) ]]; then THREADS="${BASH_REMATCH[1]}"; fi
        if [[ "$exp_file" =~ _b([0-9]+) ]]; then BLOCKS="${BASH_REMATCH[1]}"; fi

        test_id="${base_name}_t${THREADS}_b${BLOCKS}"
        error_log="$DIFF_DIR/${test_id}_error.log"

        run_emulator_capture "$INPUT_TO_USE" "$THREADS" "$BLOCKS"
        grep -E '^0x000[0-9a-fA-F]{5}[[:space:]]' "$MEMINIT_PATCHED" > "$INSTR_PART" 2>/dev/null || true

        if [ "$DRY_RUN" = "1" ]; then
            save_dry_run_output "$test_id" "$exp_file"
            continue
        fi

        if [ "$EMULATOR_EXIT" -ne 0 ] || [ ! -f "$EMU_OUTPUT" ]; then
            echo -e "${RED}[RUN FAIL]${NC} $base_name (t=$THREADS, b=$BLOCKS)"
            cat "$TEMP_CMD_LOG" > "$error_log"
            cp "$MEMINIT_PATCHED" "$DIFF_DIR/${test_id}_meminit.hex"
            ((FAIL_COUNT++))
            continue
        fi

        # Build FINAL_EXPECTED = instruction part + expected output
        cat "$INSTR_PART" "$exp_file" > "$FINAL_EXPECTED"
        sort_hex_by_addr "$EMU_OUTPUT"
        sort_hex_by_addr "$FINAL_EXPECTED"

        compare_hex_against_expected "$error_log"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[PASS]${NC}     $base_name (t=$THREADS, b=$BLOCKS)"
            rm -f "$error_log"
            ((PASS_COUNT++))
        else
            echo -e "${RED}[FAIL]${NC}     $base_name (t=$THREADS, b=$BLOCKS)"
            cp "$EMU_OUTPUT" "$DIFF_DIR/${test_id}_gen.hex"
            cp "$FINAL_EXPECTED" "$DIFF_DIR/${test_id}_exp.hex"
            cp "$MEMINIT_PATCHED" "$DIFF_DIR/${test_id}_meminit.hex"
            cp "$TEMP_CMD_LOG" "$DIFF_DIR/${test_id}_trace.log"
            ((FAIL_COUNT++))
        fi
    done
fi

# ==========================================
# Cleanup (never delete user's input file)
# ==========================================
rm -f "$MEMINIT" "$MEMINIT_PATCHED" "$EMU_OUTPUT" "$FINAL_EXPECTED" "$TEMP_CMD_LOG" "$INSTR_PART"

echo "========================================"
echo "Summary"
echo -e "Passed:  ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed:  ${RED}$FAIL_COUNT${NC}"
echo -e "No Ref:  ${YELLOW}$MISSING_COUNT${NC}"

if [ $FAIL_COUNT -gt 0 ]; then
    echo "Check '$DIFF_DIR/' for logs and generated output."
    exit 1
fi
exit 0
