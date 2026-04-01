# Register Allocation and Packetization

This document explains the register allocation and instruction packetization passes in the compiler. These passes work closely together to map virtual registers to physical registers and then bundle independent instructions into packets to exploit Instruction-Level Parallelism (ILP).

## 1. Overall Workflow

The pipeline executes in the following order (as seen in `packetization.py`):
1. **Parsing & CFG Construction**: The raw assembly is parsed into `BasicBlock` and `Instruction` representations, and control flow edges are established.
2. **Register Allocation**: A global Chaitin-style graph-coloring register allocator runs. It uses specialized ILP-friendly techniques such as live-range splitting and round-robin color selection.
3. **Data Dependence Graph (DDG) Construction**: Local data dependencies (RAW, WAW, WAR, and Memory) are analyzed within each basic block.
4. **Instruction Packetization**: A greedy list-scheduling pass forms bundles (packets) of independent instructions based on the DDG.

---

## 2. Register Allocation (`reg_alloc.py`)

The register allocator maps virtual registers from the parsed assembly to a fixed set of physical registers (e.g., `x1` to `x31`, with `x0` hardwired to zero). It aims to limit the accidental introduction of false dependencies to maximize the available parallelism for the packetizer.

### Live Range Splitting
Before standard allocation begins, the allocator performs **Live Range Splitting** across the CFG:
* It identifies disjoint def-use "webs" (independent uses of the same virtual register name) and renames them to distinct virtual registers (e.g., `_w0`, `_w1`).
* This breaks false dependencies (Write-After-Write and Write-After-Read) that were artifactually present in the original virtual register assignments, freely exposing more ILP.

### Liveness Analysis & Interference Graph
* **Liveness Analysis**: Computes globally accurate `live_in` and `live_out` sets for every basic block using a traditional backward-iterative dataflow equation.
* **Interference Graph**: Constructed by walking backward through each block and adding interference edges between any defined register and all other concurrently live registers.

### Graph Coloring (Chaitin's Algorithm)
* The allocator iteratively simplifies the graph by removing nodes with a degree smaller than the available number of physical registers. Node removals are tracked on a stack.
* If all remaining nodes have a high degree, a heuristic picks a node to "Optimistically Spill" (currently, it pushes it to the stack in hopes that coalesced neighbor colors will still leave an opening).
* **Round-Robin Assignment**: During the coloring (popping from the stack), rather than deterministically picking the first available caller-saved register, the allocator iterates through physical registers in a **round-robin fashion**. This drastically reduces the reuse of physical registers across independent instruction chains, preventing the re-introduction of false WAW/WAR dependencies and maintaining maximum ILP.

---

## 3. Data Dependence Graph (`ddg.py`)

After registers are allocated, a local Data Dependence Graph is constructed for each basic block to enforce correct execution order during packetization.

The DDG tracks the following dependencies:
* **RAW (Read-After-Write)**: True dependencies where an instruction reads a physical register defined by a prior instruction.
* **WAW (Write-After-Write)**: False dependencies where two instructions write to the same physical register.
* **WAR (Write-After-Read)**: False dependencies where an instruction overwrites a physical register before a prior instruction has read it.
* **Memory Dependencies**: Basic serialization is applied to memory instructions. Successive `sw` (Store Word) instructions are linked by `WAW(MEM)`, and reads/writes are linked by `RAW(MEM)` and `WAR(MEM)` edges. Currently, memory is treated as a single monolithic resource.

---

## 4. Packetization (`packetization.py`)

The packetizer is responsible for grouping instructions into explicitly parallel execution bundles (packets) up to a hardware-defined `max_packet_size` (e.g., VLIW width).

### Greedy Scheduling
It uses a straightforward greedy scheduling algorithm within the confines of each basic block:
1. **Readiness Checking**: It queries the DDG's `backward_edges` to find instructions whose dependencies have all been completely resolved (i.e., their prerequisite instructions have already been assigned to an earlier packet).
2. **Packet Formation**: It selects up to `max_packet_size` ready instructions and unconditionally bundles them together into a new packet.
3. **Commitment**: The newly packetized instructions are added to the `scheduled_set`, potentially making subsequent dependent instructions ready for the next packet.
4. The process repeats until all instructions in the basic block have been scheduled.
