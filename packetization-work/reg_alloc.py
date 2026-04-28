import sys
import re

# TWIG Architecture ABI Pinned Variables
RESERVED_REGS = {
    "x0",
    "x1",
    "x2",
    "x3",
    "x4",
    "x5",
    "x6",
    "x7",
    "x8",
    "x28",
    "x29",
    "x30",
    "x31",
    "x63",
}


def compute_liveness(blocks):
    """
    computes DEF and USE sets, then calculates LIVE_IN and LIVE_OUT
    for each basic block.
    """
    for b in blocks:
        b.def_set = set()
        b.use_set = set()
        for inst in b.instructions:
            for src in inst.srcs:
                if src not in b.def_set and src not in RESERVED_REGS:
                    b.use_set.add(src)
            if inst.dest and inst.dest not in RESERVED_REGS:
                b.def_set.add(inst.dest)

        b.live_in = set()
        b.live_out = set()

    changed = True
    while changed:
        changed = False
        # apparently reverse order converges faster
        for b in reversed(blocks):
            old_in = b.live_in.copy()
            old_out = b.live_out.copy()

            b.live_out = set()
            for succ in b.successors:
                b.live_out.update(succ.live_in)

            b.live_in = b.use_set.union(b.live_out - b.def_set)

            if old_in != b.live_in or old_out != b.live_out:
                changed = True


def estimate_loop_depths(blocks):
    """
    Estimates loop nesting depth for each block by counting
    back-edges (predecessor that appears at or after this block in
    textual order). Each back-edge targeting a block adds one
    nesting level.
    """
    b_idx_map = {b.name: i for i, b in enumerate(blocks)}
    depths = {}
    for b in blocks:
        depth = 0
        for pred in b.predecessors:
            pred_idx = b_idx_map.get(pred.name)
            b_idx = b_idx_map.get(b.name)
            if (
                pred_idx is not None
                and b_idx is not None
                and pred_idx >= b_idx
            ):
                depth += 1
        depths[b.name] = depth
    return depths


def calculate_spill_costs(blocks):
    """
    Computes a static frequency cost for each virtual variable.

    Two improvements over a naive counter:
      1. Loop depth is exponential: weight = 10^depth. A variable
         in a doubly-nested loop is 100x more expensive to spill
         than one outside any loop.
      2. Uses are weighted 2x vs defs, because spilling a use
         inserts a load (latency penalty) while spilling a def
         inserts a store (cheaper on most architectures).
    """
    costs = {}
    depths = estimate_loop_depths(blocks)

    for b in blocks:
        weight = 10 ** depths.get(b.name, 0)

        for inst in b.instructions:
            for s in inst.srcs:
                if s not in RESERVED_REGS:
                    costs[s] = costs.get(s, 0) + 2 * weight
            if inst.dest and inst.dest not in RESERVED_REGS:
                costs[inst.dest] = costs.get(inst.dest, 0) + weight

    return costs


def build_interference_graph(blocks):
    adj_list = {}

    def add_edge(u, v):
        if u in RESERVED_REGS or v in RESERVED_REGS:
            return  # never put reserved regs in the interference graph
        if u not in adj_list:
            adj_list[u] = set()
        if v not in adj_list:
            adj_list[v] = set()
        if u != v:
            adj_list[u].add(v)
            adj_list[v].add(u)

    for b in blocks:
        live = b.live_out.copy()
        for inst in reversed(b.instructions):
            if inst.dest and inst.dest not in RESERVED_REGS:
                live.discard(inst.dest)
                if inst.dest not in adj_list:
                    adj_list[inst.dest] = set()
                for lreg in live:
                    if lreg not in RESERVED_REGS:
                        add_edge(inst.dest, lreg)

            for src in inst.srcs:
                if src not in RESERVED_REGS:
                    live.add(src)
                    if src not in adj_list:
                        adj_list[src] = set()

    return adj_list


def color_graph(adj_list, num_registers, spill_costs=None):
    """
    Chaitin's
    Colors from x1 to x{num_registers-1}. x0 is hardwired.
    """
    colors_available = [
        f"x{i}"
        for i in range(1, num_registers)
        if f"x{i}" not in RESERVED_REGS
    ]
    num_colors = len(colors_available)

    stack = []
    spilled_nodes = []
    if spill_costs is None:
        spill_costs = {}
    # make a destructible copy of the graph
    current_graph = {u: set(v) for u, v in adj_list.items()}
    degrees = {u: len(v) for u, v in current_graph.items()}

    while current_graph:
        node_to_remove = None
        # find a node with degree < available colors
        for node, degree in degrees.items():
            if degree < num_colors:
                node_to_remove = node
                break

        if node_to_remove is None:
            # spill: pick node that minimizes Cost / Degree
            spill_node = min(
                degrees,
                key=lambda n: (spill_costs.get(n, 1) / float(degrees[n])),
            )
            print(
                f"Warning: Potential spill for {spill_node} (Cost: {spill_costs.get(spill_node, 1)}, Degree: {degrees[spill_node]})"
            )
            # TODO: iterative spilling phase should be implemented here modifying the block AST
            # optimistic coloring: we push it to the stack anyway; it might get a color if its neighbors share colors.
            node_to_remove = spill_node

        stack.append(node_to_remove)

        # remove node and its edges from the temporary graph
        for neighbor in current_graph[node_to_remove]:
            current_graph[neighbor].remove(node_to_remove)
            degrees[neighbor] -= 1

        del current_graph[node_to_remove]
        del degrees[node_to_remove]

    allocation = {}

    # spread colors using round-robin to maximize ILP
    # by minimizing false WAW and WAR dependencies on physical registers
    last_color_idx = 0

    while stack:
        node = stack.pop()
        used_colors = set()
        for neighbor in adj_list[node]:
            if neighbor in allocation:
                used_colors.add(allocation[neighbor])

        possible_colors = [c for c in colors_available if c not in used_colors]

        if possible_colors:
            # round robin selection
            chosen_color = None
            for i in range(num_colors):
                idx = (last_color_idx + i) % num_colors
                candidate = colors_available[idx]
                if candidate in possible_colors:
                    chosen_color = candidate
                    last_color_idx = (idx + 1) % num_colors
                    break

            if chosen_color:
                allocation[node] = chosen_color
            else:
                allocation[node] = possible_colors[0]  # Fallback
        else:
            spilled_nodes.append(node)

    if spilled_nodes:
        return None, spilled_nodes
    return allocation, []


def rewrite_instructions(blocks, allocation):
    """
    rewrites the instruction operands based on the final coloring map.
    """
    for b in blocks:
        for inst in b.instructions:
            for old, new in allocation.items():
                if old in inst.original_text:
                    inst.original_text = re.sub(
                        rf"\b{old}\b", new, inst.original_text
                    )

            if inst.dest and inst.dest not in RESERVED_REGS:
                inst.dest = allocation[inst.dest]

            new_srcs = set()
            for src in inst.srcs:
                if src in RESERVED_REGS:
                    new_srcs.add(src)
                else:
                    new_srcs.add(allocation[src])
            inst.srcs = new_srcs


def split_live_ranges(blocks):
    """
    renames disjoint def-use webs into distinct virtual registers.
    breaks false dependencies (WAW, WAR) and exposes more ILP.
    """
    # get all vars
    all_regs = set()
    for b in blocks:
        for inst in b.instructions:
            all_regs.update([s for s in inst.srcs if s not in RESERVED_REGS])
            if inst.dest and inst.dest not in RESERVED_REGS:
                all_regs.add(inst.dest)

    # renaming based on liveness
    entry_defs = {reg: f"def_entry_{reg}" for reg in all_regs}

    for b in blocks:
        b.rd_in = {}
        b.rd_out = {}
        b.rd_gen = {}
        for i, inst in enumerate(b.instructions):
            if inst.dest and inst.dest not in RESERVED_REGS:
                b.rd_gen[inst.dest] = f"def_{b.name}_{i}_{inst.dest}"

    changed = True
    while changed:
        changed = False
        for i, b in enumerate(blocks):
            old_in = {k: set(v) for k, v in b.rd_in.items()}
            old_out = {k: set(v) for k, v in b.rd_out.items()}

            new_in = {}
            if not b.predecessors and i == 0:
                for reg, d in entry_defs.items():
                    new_in[reg] = {d}

            for pred in b.predecessors:
                for reg, defs in pred.rd_out.items():
                    if reg not in new_in:
                        new_in[reg] = set()
                    new_in[reg].update(defs)
            b.rd_in = new_in

            new_out = {}
            for reg in all_regs:
                if reg in b.rd_gen:
                    new_out[reg] = {b.rd_gen[reg]}
                elif reg in b.rd_in:
                    new_out[reg] = set(b.rd_in[reg])
            b.rd_out = new_out

            if old_in != b.rd_in or old_out != b.rd_out:
                changed = True

    parent = {}

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    for reg, d in entry_defs.items():
        parent[d] = d
    for b in blocks:
        for i, inst in enumerate(b.instructions):
            if inst.dest and inst.dest not in RESERVED_REGS:
                d = f"def_{b.name}_{i}_{inst.dest}"
                parent[d] = d

    # connect uses to defs
    for b in blocks:
        current_defs = {reg: set(defs) for reg, defs in b.rd_in.items()}
        for i, inst in enumerate(b.instructions):
            for src in inst.srcs:
                if src not in RESERVED_REGS:
                    reaching = list(current_defs.get(src, []))
                    if reaching:
                        for other_def in reaching[1:]:
                            union(reaching[0], other_def)

            if inst.dest and inst.dest not in RESERVED_REGS:
                d = f"def_{b.name}_{i}_{inst.dest}"
                current_defs[inst.dest] = {d}
    # ============================================================
    # Memory-flow web coalescing
    # ============================================================
    # When a value is stored to a memory slot and later loaded back
    # from the same slot with no intervening store to that slot, the
    # use feeding the `sw` and the def produced by the `lw` are the
    # same logical value. Union their webs so the allocator gives
    # them the same physical register.
    #
    # This is a pure dataflow rule - it has no notion of "callee
    # saved" or "ABI". It just observes that bytes round-trip through
    # memory unchanged.
    #
    # Pattern matched: sw <reg>, <imm>(<base>) ... lw <reg>, <imm>(<base>)
    # where <base> is x2 (SP) or x8 (FP) so the slot identity is
    # stable, and the slot is not written between the sw and the lw.
    # ============================================================

    sw_lw_re = re.compile(
        r"^\s*(sw|lw)\s+(\w+)\s*,\s*(-?\d+)\s*\(\s*(x\d+)\s*\)"
    )

    def parse_mem_op(inst):
        """Returns (op, reg, offset, base) or None for non-stack mem ops."""
        m = sw_lw_re.match(inst.original_text)
        if not m:
            return None
        op, reg, offset, base = (
            m.group(1),
            m.group(2),
            int(m.group(3)),
            m.group(4),
        )
        if base not in {"x2", "x8"}:  # only frame-relative
            return None
        return (op, reg, offset, base)

    # Walk the program in textual order, tracking the most recent sw
    # to each (offset, base) slot. When a matching lw is found, union
    # the sw's source-web with the lw's dest-web.
    last_store = {}  # (offset, base) -> (src_web, store_index_in_program)

    for b in blocks:
        current_defs = {reg: set(defs) for reg, defs in b.rd_in.items()}
        for i, inst in enumerate(b.instructions):
            mop = parse_mem_op(inst)

            if mop is not None:
                op, reg, offset, base = mop
                slot_key = (offset, base)

                if op == "sw":
                    # Source register's reaching def feeds this store.
                    reaching = list(current_defs.get(reg, []))
                    if reaching and reg not in RESERVED_REGS:
                        last_store[slot_key] = reaching[0]
                    elif reg in RESERVED_REGS:
                        # The stored value is the entry-def of a reserved reg.
                        # Use a synthetic web key for it so we can union later.
                        last_store[slot_key] = f"def_entry_{reg}"
                        if last_store[slot_key] not in parent:
                            parent[last_store[slot_key]] = last_store[slot_key]

                elif op == "lw":
                    # Match against the most recent store to this slot.
                    if slot_key in last_store and reg not in RESERVED_REGS:
                        load_def = f"def_{b.name}_{i}_{reg}"
                        if (
                            load_def in parent
                            and last_store[slot_key] in parent
                        ):
                            union(last_store[slot_key], load_def)

            # Maintain register-level current_defs for non-mem instructions too,
            # so we can find the right reaching def when an `sw` comes along.
            if inst.dest and inst.dest not in RESERVED_REGS:
                d = f"def_{b.name}_{i}_{inst.dest}"
                current_defs[inst.dest] = {d}

            # If this instruction writes the slot's base register or
            # stores to the same slot (already handled above), invalidate
            # tracking. For now, only `sw` to the slot matters - any
            # intervening `sw` to (offset, base) replaces last_store, which
            # the `op == "sw"` branch handles. Writes to the base register
            # x2/x8 itself are rare in user code (only prologue/epilog).

            # If the base register itself is rewritten, all slots become
            # ambiguous. Conservative: invalidate.
            if inst.dest in {"x2", "x8"}:
                last_store = {
                    k: v for k, v in last_store.items() if k[1] != inst.dest
                }

    # ============================================================
    # End memory-flow coalescing
    # ============================================================
    web_names = {}
    for d in parent:
        root = find(d)
        if root not in web_names:
            parts = root.split("_")
            orig_reg = parts[-1]
            web_names[root] = f"{orig_reg}_w{len(web_names)}"

    for b in blocks:
        current_defs = {reg: set(defs) for reg, defs in b.rd_in.items()}
        for i, inst in enumerate(b.instructions):
            tokens = re.split(r"(\W+)", inst.original_text)

            # map old src -> new web name for this specific instruction instance
            src_map = {}
            new_srcs = set()
            for src in inst.srcs:
                if src in RESERVED_REGS:
                    new_srcs.add(
                        src
                    )  # keep reserved regs as-is; don't rename, but DO track
                    continue
                reaching = list(current_defs.get(src, []))
                if reaching:
                    web = web_names[find(reaching[0])]
                    new_srcs.add(web)
                    src_map[src] = web
                else:
                    new_srcs.add(src)

            # identify new dest
            new_dest = None
            if inst.dest and inst.dest not in RESERVED_REGS:
                d = f"def_{b.name}_{i}_{inst.dest}"
                current_defs[inst.dest] = {d}
                web = web_names[find(d)]
                new_dest = web

            dest_replaced = False
            for t_idx, t in enumerate(tokens):
                if t == inst.dest and not dest_replaced and new_dest:
                    tokens[t_idx] = new_dest
                    dest_replaced = True
                elif t in src_map:
                    tokens[t_idx] = src_map[t]

            inst.original_text = "".join(tokens)
            inst.dest = new_dest if new_dest else inst.dest
            inst.srcs = new_srcs


def insert_spill_code(blocks, spilled_nodes, spill_state):
    from ddg import Instruction

    spill_counter = 0
    spill_offsets, next_offset = spill_state
    for node in spilled_nodes:
        if node not in spill_offsets:
            spill_offsets[node] = next_offset
            next_offset += 4

    spilled_set = set(spilled_nodes)

    for b in blocks:
        new_instructions = []
        for inst in b.instructions:

            # 1) If an instruction USES a spilled node
            used_spills = [s for s in inst.srcs if s in spilled_set]
            for s in used_spills:
                spill_counter += 1
                temp_reg = f"{s}_use{spill_counter}"
                offset = spill_offsets[s]

                # Create a load instruction BEFORE the use
                load_text = f"lw {temp_reg}, {offset}(x0)"
                load_idx = len(new_instructions)
                load_inst = Instruction(load_idx, load_text)
                new_instructions.append(load_inst)

                # Replace the use in the original instruction
                inst.original_text = re.sub(
                    rf"\b{s}\b", temp_reg, inst.original_text
                )
                inst.srcs.remove(s)
                inst.srcs.add(temp_reg)

            # Re-index the original instruction
            inst.id = len(new_instructions)
            new_instructions.append(inst)

            # 2) If an instruction DEFINES a spilled node
            if inst.dest in spilled_set:
                spill_counter += 1
                temp_reg = f"{inst.dest}_def{spill_counter}"
                offset = spill_offsets[inst.dest]

                # Replace the define in the original instruction
                inst.original_text = re.sub(
                    rf"\b{inst.dest}\b", temp_reg, inst.original_text
                )
                inst.dest = temp_reg

                # Create a store instruction AFTER the def
                store_text = f"sw {temp_reg}, {offset}(x0)"
                store_idx = len(new_instructions)
                store_inst = Instruction(store_idx, store_text)
                new_instructions.append(store_inst)

        b.instructions = new_instructions

    return (spill_offsets, next_offset)


def allocate_registers_chaitin(blocks, num_registers=64):
    print("\n--- Live Range Splitting Phase ---")
    split_live_ranges(blocks)

    max_iter = 10
    iteration = 0
    spill_state = ({}, 1024)  # (offset_map, next_offset)
    while True:
        spill_costs = calculate_spill_costs(blocks)
        compute_liveness(blocks)
        adj_list = build_interference_graph(blocks)

        # debugging below
        print("Reserved regs in adj_list (should be empty):")
        for k in adj_list:
            if k in RESERVED_REGS:
                print(f"  {k}: {adj_list[k]}")
        # debugging above

        print(f"--- Register Allocation Phase (Iter {iteration}) ---")
        print(f"Extracted {len(adj_list)} Virtual Variables")

        allocation, spilled_nodes = color_graph(
            adj_list, num_registers, spill_costs
        )

        # debugging below
        print(
            "Allocation entries that map to reserved regs (should be empty):"
        )
        for web, phys in allocation.items():
            if phys in RESERVED_REGS:
                print(f"  {web} -> {phys}")
        # debugging above

        if not spilled_nodes:
            rewrite_instructions(blocks, allocation)

            # verification
            valid = True
            for u in adj_list:
                for v in adj_list[u]:
                    if allocation.get(u) == allocation.get(v):
                        print(
                            f"VERIFICATION FAILED: {u} and {v} interfere but both got {allocation[u]}"
                        )
                        valid = False

            if valid:
                print(
                    "Verification: SUCCESS (No interfering variables share the same physical register)"
                )

            print("Allocation Map: ", allocation)
            print("--- End Register Allocation ---")
            break
        else:
            print(f"Spilling nodes: {spilled_nodes}")
            spill_state = insert_spill_code(blocks, spilled_nodes, spill_state)
            iteration += 1
            if iteration > max_iter:
                raise Exception(
                    "Exceeded max iterations for spilling. Graph won't color."
                )
