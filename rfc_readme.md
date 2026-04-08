## RFC Implementation

### 1) RFC logic integrated into register allocation
File: `ppci/codegen/registerallocator.py`

Added an RFC pre-assignment phase inside `GraphColoringRegisterAllocator`:

- **`self.frame.cfg = cfg` in `init_data()`**
  - Stores the computed flow graph on the frame so live-range info can be reused by RFC scoring.

- **`self.rfc_node_assignment = self._build_rfc_allocation()`**
  - Runs once per allocation round after IG/liveness/worklists are built.
  - Produces a map `{interference_node -> reserved_rfc_register}`.

- New helper methods:
  - **`_get_rfc_reserved_entries()`**
    - Reads `arch.rfc_reserved_registers`.
    - Groups reserved regs by register class.
  - **`_get_node_live_range(node)`**
    - Estimates live range length per IG node.
    - Uses CFG live-range segments when present; falls back to use/def counts.
  - **`_get_node_energy_savings(node)`**
    - Calls architecture hook `arch.get_rfc_energy_savings(frame, node)`.
  - **`_rfc_entry_available(rfc_entry, node, chosen)`**
    - Checks class compatibility and interference safety for reusing same RFC entry.

- **`_build_rfc_allocation()` implements your pseudocode**
  - Iterates virtual register instances (IG nodes).
  - Computes:
    - `averageSavings = getEnergySavings(registerInstance) / getLiveRange(registerInstance)`
  - Pushes only positive-savings nodes into a max-priority queue.
  - Pops highest priority first and greedily allocates to first compatible RFC entry.

- **`assign_colors()` integration**
  - Before normal color selection, checks if node is in `self.rfc_node_assignment`.
  - If yes, directly assigns that RFC physical register and skips regular pool coloring.
  - This is what makes RFC-chosen values actually land in RFC-reserved architectural regs.

---

### 2) Reserved RFC registers removed from MRF allocatable pool
File: `ppci/arch/twig/registers.py`

Added explicit split between MRF and RFC:

- **`RFC_RESERVED_REGS = (R61, R62)`**
  - These are “stolen” for RFC use.

- Created `MRF_ALLOCATABLE_REGS` by removing reserved regs from the previous general pool.

- Updated Twig register class:
  - `register_classes_swfp` now uses `MRF_ALLOCATABLE_REGS` instead of the old hardcoded list.
  - Effect: normal graph coloring cannot assign `R61/R62` unless RFC logic does it.

This directly satisfies your requirement that some architectural regs are no longer part of the normal MRF allocator set.

---

### 3) Arch-level RFC hook + energy model
File: `ppci/arch/twig/arch.py`

Added architecture-facing RFC controls:

- **`self.rfc_reserved_registers = RFC_RESERVED_REGS`**
  - Exposes reserved entries to allocator.

- Removed `R61` and `R62` from `caller_save`
  - Keeps ABI/clobber metadata consistent with RFC-only ownership.

- Implemented **`get_rfc_energy_savings(frame, node)`** with your formula and constants:
  - `savings = (MRF.write - RFC.write) + (MRF.read - RFC.read) * num_reads`
  - Constants used:
    - MRF write = `0.0322`
    - MRF read = `0.0208`
    - RFC write = `0.0034`
    - RFC read = `0.0033`
  - `num_reads` is computed from interference graph uses:
    - sum of `len(frame.ig.uses(tmp))` across temps in that node.

This is the architecture-specific “getEnergySavings(registerInstance)” piece from your algorithm.

---

## How the pieces work together (end-to-end)

For each function frame:

1. `CodeGenerator` calls `register_allocator.alloc_frame(frame)`.
2. RA builds CFG + liveness + interference graph in `init_data()`.
3. RA calls `_build_rfc_allocation()`:
   - Reads RFC entries from `TwigArch.rfc_reserved_registers`.
   - Scores each candidate IG node using `TwigArch.get_rfc_energy_savings(...) / live_range`.
   - Priority-queues positive candidates.
   - Allocates highest-priority candidates to reserved RFC entries with interference checks.
4. RA continues normal coalescing/simplify/spill process.
5. During `assign_colors()`:
   - RFC-picked nodes are fixed to `R61/R62`.
   - Everything else colored from MRF allocatable set (which excludes `R61/R62`).

So RFC is now a constrained high-priority sub-allocation layered into existing RA, while regular RA remains unchanged for non-RFC assignments.

---

## Testing and verification done

### Executed tests
Ran:
- `python3 -m pytest test/codegen/test_register_allocator.py`

Result:
- **9/9 tests passed** (both before and after energy-model insertion)

### Lint checks
Ran lint diagnostics on edited files:
- `ppci/codegen/registerallocator.py`
- `ppci/arch/twig/registers.py`
- `ppci/arch/twig/arch.py`

Result:
- **No linter errors**

### What these validations prove
- Existing allocator behavior and invariants were not broken by RFC integration.
- Changes compile and pass current RA unit coverage.
- No style/diagnostic regressions in modified files.

### What is still not explicitly tested yet
Current tests are generic allocator tests; they do **not** yet assert Twig RFC-specific behavior. Missing dedicated tests include:
- `R61/R62` never used by normal MRF allocation.
- RFC assignment happens for positive savings nodes.
- RFC assignment respects interference for shared RFC entries.
- RFC-off / empty-reserved-reg scenarios.

---

## Packetization-Work Alignment Update

To align with the packetization prototype flow in `packetization-work/`, the RFC work was also integrated there so both code paths reflect the same intent.

### 1) RFC-aware allocation added to `packetization-work/reg_alloc.py`

- Added RFC energy constants and reserved entries:
  - `MRF_WRITE_COST_NJ = 0.0322`
  - `MRF_READ_COST_NJ = 0.0208`
  - `RFC_WRITE_COST_NJ = 0.0034`
  - `RFC_READ_COST_NJ = 0.0033`
  - `DEFAULT_RFC_ENTRIES = ("x61", "x62")`
- Added `_compute_register_metrics(blocks)` to estimate:
  - `num_reads` per virtual register
  - `live_range` span per virtual register
- Added `_get_energy_savings(num_reads)` implementing:
  - `(MRF.write - RFC.write) + (MRF.read - RFC.read) * num_reads`
- Added `allocate_rfc_registers(...)`:
  - Builds priority queue with `averageSavings = energySavings / liveRange`
  - Keeps only positive priorities
  - Greedily maps best candidates onto RFC entries with interference checks
- Extended `color_graph(...)` to support:
  - `reserved_registers` (exclude RFC regs from normal MRF pool)
  - `precolored` (force RFC assignments)
- Extended `allocate_registers_chaitin(...)`:
  - RFC pre-assignment first
  - regular coloring second
  - defaults to `num_registers=64` for Twig-like register naming

### 2) Packetization/RA ordering updated in `packetization-work/packetization.py`

The prototype pipeline now does:

1. Parse ASM (`parse_asm`)
2. Initial packetization on virtual registers
3. Reorder block instructions by packet schedule (`reorder_block_by_packets`)
4. Rebuild DDG
5. Run Chaitin RA with RFC (`allocate_registers_chaitin(..., enable_rfc=True)`)
6. Rebuild DDG again
7. Packetize/print final post-RA packets

This ordering was intentionally changed so RFC assignment is based on packetized instruction order, matching the requested direction for WAR-risk reduction.

### 3) Scope clarification

- Main compiler path (`ppci/codegen/...`) still performs RA before stream-time packetization.
- `packetization-work/` now reflects the “packetize before RFC-aware RA” strategy.
- These two paths are currently separate implementations; they are aligned in RFC policy (energy/live-range queue + reserved RFC regs), but not yet unified into one compiler pipeline.

### 4) Validation of this update

- Syntax checks passed for all prototype files:
  - `python3 -m py_compile packetization-work/reg_alloc.py packetization-work/ddg.py packetization-work/packetization.py`
