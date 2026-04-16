# GPUTest / emulator-test

---

| Producer | Output (concept) |
|----------|------------------|
| **Compiler** | **Program**: instructions as **`kernel.hex`** (flat words) + **`build/*.stack.json`**, **`.bin`**, etc. |
| **`cpu_sim` / benchmark** (`make data-*`, **`datacopy`**) | **Reference I/O**: **`kernel_data.hex`** (initial RAM / inputs), **`kernel_exp_tN_bM.hex`** (golden memory after CPU run for **N** threads, **M** blocks). |
| **Emulator** (`cardinal-ISS`) | **Actual run**: loads a merged image, executes, dumps **`memsim.hex`** (post-run memory; stack range may be omitted from dump). |

---

| File / pattern | From | Does |
|----------------|------|------|
| **`tests/complex_tests/<k>/<k>.hex`** | Compiler (`make build-<k>`) | Kernel **instruction** image (flat hex words). |
| **`<k>_data.hex`** | CPU sim / benchmark → **`datacopy`** | **Initial data** appended to meminit (buffers, params, `bb_size`, …). |
| **`<k>_exp_tN_bM.hex`** | CPU sim golden | **Expected data words** for launch **t=N, b=M** (not the program bytes). |
| **`build/meminit-<k>.hex`** | **Makefile**: `awk` on **`<k>.hex`** + cat **`_data.hex`** | **Single RAM image** for **`make run`**: addressed code at `0x00000000…` + data at high addresses. |
| **`memsim.hex`** | Emulator **atexit** dump | **Result** memory (`0xADDR 0xDATA`); zeros mostly skipped; optional **stack strip** via **`emu_run_flags.py`** + **`.stack.json`**. |
| **`test_hex.sh`** input | Same tree as above | Builds working **meminit**, runs emu, compares output to **expected**. |

---

1. **`INSTR_PART`**: instruction-region lines from the **input** (addrs `0x0…` / `0x1…`).
2. **`FINAL_EXPECTED`**: **`INSTR_PART`** + matching **`_exp_tN_bM.hex`** → sorted.
3. Compare **`memsim.hex`** vs **`FINAL_EXPECTED`**:
   - Default: **`diff -u`** (exact words).
   - **`RELAX_FP_HEX=1`**: **`tests/hex_mem_compare.py`** — only addresses **in the expected file** must match; data ≥ `0x20000000` uses **float tolerance** (`isclose`); pointers still exact. Used for **vertexShader** / **triangle** tests in the Makefile.

**`tests/diffs.py`** (`make diffs`): offline **address diffs** between saved **`_gen` / `_exp` / `_meminit`** under **`test_diffs/`** — **not** the pass/fail gate.

---

## Thread counts

- Filenames encode launch: **`_exp_t961_b1.hex`** ⇒ emulator must run **`-t 961 -b 1`** for that golden.
- **Triangle**: **31×31 = 961** threads (matches **`triangle_data.hex`** / `bb_size`).
- **Pixel**: **32×32 = 1024** threads; golden **`_t1024_b1`**.
- **Default `32`**: many simple kernels use **`t32_b1`** unless overridden.

---

## Emulator instrumentation (optional)

| Mechanism | Role |
|-----------|------|
| **`--count` / `dyn_instr_stats.py`** | Dynamic opcode counts (per warp / lane-weighted). |
| **`--mem-hist` / `mem_access_hist.py`** | Byte-touch histogram → **JSON** + **PNG**; **`MEMACCESS*`** in **`emulator-test/Makefile`**. |
| **`--mem-coal` / `mem_coalescing.py`** | Coalescing-style histogram **PNG**; **`MEMCOAL=1`** → **`build/<KERNEL>_memcloalescing.png`**. |
| **`emu_run_flags.py`** | Prints **`--arg-pointer`** (first addr ≥ `0x20000000`) and stack flags from **`.stack.json`**. |

---

## Benchmark

- **`benchmark/cpu_sim`**: reference runs; **`PIXEL_PRINT_DEBUG`**, **`saxpy_main.c`** hex correctness — feed **`datacopy`** / **`data-pixel`** / **`data-saxpy`**.
- **`tests/saxpy_relocate.py`**: maps saxpy CPU dumps into the layout the GPU test expects.
