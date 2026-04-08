import sys
import re
import heapq


MRF_WRITE_COST_NJ = 0.0322
MRF_READ_COST_NJ = 0.0208
RFC_READ_COST_NJ = 0.0033
RFC_WRITE_COST_NJ = 0.0034
DEFAULT_RFC_ENTRIES = ("x61", "x62")

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
                if src not in b.def_set and src != "x0":
                    b.use_set.add(src)
            if inst.dest and inst.dest != "x0":
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

def build_interference_graph(blocks):
    """
    constructs the register interference graph using backward traversal
    within each block
    """
    adj_list = {}

    def add_edge(u, v):
        if u not in adj_list: adj_list[u] = set()
        if v not in adj_list: adj_list[v] = set()
        if u != v:
            adj_list[u].add(v)
            adj_list[v].add(u)

    for b in blocks:
        live = b.live_out.copy()
        for inst in reversed(b.instructions):
            if inst.dest and inst.dest != "x0":
                live.discard(inst.dest)
                if inst.dest not in adj_list:
                    adj_list[inst.dest] = set()
                # defined register interferes with all currently live registers
                for lreg in live:
                    add_edge(inst.dest, lreg)

            for src in inst.srcs:
                if src != "x0":
                    live.add(src)
                    if src not in adj_list:
                        adj_list[src] = set()

    return adj_list

def color_graph(adj_list, num_registers, reserved_registers=(), precolored=None):
    """
    Chaitin's
    Colors from x1 to x{num_registers-1}. x0 is hardwired.
    """
    colors_available = [
        f"x{i}"
        for i in range(1, num_registers)
        if f"x{i}" not in set(reserved_registers)
    ]
    num_colors = len(colors_available)

    stack = []
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
            # spill: if we can't simplify, we heuristically pick a node to spill (max degree for now)
            spill_node = max(degrees, key=degrees.get)
            print(f"Warning: Potential spill for {spill_node} as degree {degrees[spill_node]} >= {num_colors}.")
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

    allocation = dict(precolored or {})

    # spread colors using round-robin to maximize ILP
    # by minimizing false WAW and WAR dependencies on physical registers
    last_color_idx = 0

    while stack:
        node = stack.pop()
        if node in allocation:
            # Pre-assigned (e.g. RFC entry)
            continue
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
                allocation[node] = possible_colors[0] # Fallback
        else:
            # TODO: implement iterative spilling logic
            raise Exception(f"Failed to color node {node}. All {num_colors} registers taken by adjacent nodes. Iterative Spilling needs to be implemented here!")

    return allocation


def _compute_register_metrics(blocks):
    """Compute per-register read count and live-range span."""
    reads = {}
    first_pos = {}
    last_pos = {}
    pos = 0
    for block in blocks:
        for inst in block.instructions:
            for src in inst.srcs:
                if src == "x0":
                    continue
                reads[src] = reads.get(src, 0) + 1
                if src not in first_pos:
                    first_pos[src] = pos
                last_pos[src] = pos
            if inst.dest and inst.dest != "x0":
                reg = inst.dest
                if reg not in first_pos:
                    first_pos[reg] = pos
                last_pos[reg] = pos
            pos += 1

    metrics = {}
    all_regs = set(reads) | set(first_pos) | set(last_pos)
    for reg in all_regs:
        lr = max(1, last_pos.get(reg, 0) - first_pos.get(reg, 0) + 1)
        metrics[reg] = {"num_reads": reads.get(reg, 0), "live_range": lr}
    return metrics


def _get_energy_savings(num_reads):
    return (MRF_WRITE_COST_NJ - RFC_WRITE_COST_NJ) + (
        MRF_READ_COST_NJ - RFC_READ_COST_NJ
    ) * num_reads


def allocate_rfc_registers(
    blocks, adj_list, rfc_entries=DEFAULT_RFC_ENTRIES
):
    """Allocate profitable virtual registers into RFC-only entries.

    Policy:
      averageSavings = getEnergySavings(registerInstance) / getLiveRange(registerInstance)
      if averageSavings > 0: push to priority queue
      pop best and greedily assign first available RFC entry
    """
    metrics = _compute_register_metrics(blocks)
    queue = []
    counter = 0
    for reg in adj_list:
        if reg == "x0":
            continue
        info = metrics.get(reg, {"num_reads": 0, "live_range": 1})
        savings = _get_energy_savings(info["num_reads"])
        avg = savings / max(1, info["live_range"])
        if avg > 0:
            heapq.heappush(queue, (-avg, counter, reg))
            counter += 1

    chosen = {}
    while queue:
        _, _, reg = heapq.heappop(queue)
        for entry in rfc_entries:
            available = True
            for other_reg, other_entry in chosen.items():
                if other_entry == entry and other_reg in adj_list.get(reg, set()):
                    available = False
                    break
            if available:
                chosen[reg] = entry
                break
    return chosen

def rewrite_instructions(blocks, allocation):
    """
    rewrites the instruction operands based on the final coloring map.
    """
    for b in blocks:
        for inst in b.instructions:
            for old, new in allocation.items():
                if old in inst.original_text:
                    inst.original_text = re.sub(rf"\b{old}\b", new, inst.original_text)

            if inst.dest and inst.dest != "x0":
                inst.dest = allocation[inst.dest]

            new_srcs = set()
            for src in inst.srcs:
                if src != "x0":
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
            all_regs.update([s for s in inst.srcs if s != "x0"])
            if inst.dest and inst.dest != "x0":
                all_regs.add(inst.dest)

    # renaming based on liveness
    entry_defs = {reg: f"def_entry_{reg}" for reg in all_regs}

    for b in blocks:
        b.rd_in = {}
        b.rd_out = {}
        b.rd_gen = {}
        for i, inst in enumerate(b.instructions):
            if inst.dest and inst.dest != "x0":
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
                    if reg not in new_in: new_in[reg] = set()
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
        if parent[i] == i: return i
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
            if inst.dest and inst.dest != "x0":
                d = f"def_{b.name}_{i}_{inst.dest}"
                parent[d] = d

    # connect uses to defs
    for b in blocks:
        current_defs = {reg: set(defs) for reg, defs in b.rd_in.items()}
        for i, inst in enumerate(b.instructions):
            for src in inst.srcs:
                if src != "x0":
                    reaching = list(current_defs.get(src, []))
                    if reaching:
                        for other_def in reaching[1:]:
                            union(reaching[0], other_def)

            if inst.dest and inst.dest != "x0":
                d = f"def_{b.name}_{i}_{inst.dest}"
                current_defs[inst.dest] = {d}

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
            tokens = re.split(r'(\W+)', inst.original_text)

            # map old src -> new web name for this specific instruction instance
            src_map = {}
            new_srcs = set()
            for src in inst.srcs:
                if src != "x0":
                    reaching = list(current_defs.get(src, []))
                    if reaching:
                        web = web_names[find(reaching[0])]
                        new_srcs.add(web)
                        src_map[src] = web
                    else:
                        new_srcs.add(src)

            # identify new dest
            new_dest = None
            if inst.dest and inst.dest != "x0":
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


def allocate_registers_chaitin(
    blocks,
    num_registers=64,
    enable_rfc=True,
    rfc_entries=DEFAULT_RFC_ENTRIES,
):
    print("\n--- Live Range Splitting Phase ---")
    split_live_ranges(blocks)

    compute_liveness(blocks)
    adj_list = build_interference_graph(blocks)

    print("--- Register Allocation Phase ---")
    print(f"Extracted {len(adj_list)} Virtual Variables")

    rfc_assignment = {}
    if enable_rfc and rfc_entries:
        rfc_assignment = allocate_rfc_registers(
            blocks, adj_list, rfc_entries=rfc_entries
        )
        print(f"RFC assignments: {rfc_assignment}")

    allocation = color_graph(
        adj_list,
        num_registers,
        reserved_registers=rfc_entries,
        precolored=rfc_assignment,
    )
    rewrite_instructions(blocks, allocation)

    # verification
    valid = True
    for u in adj_list:
        for v in adj_list[u]:
            if allocation.get(u) == allocation.get(v):
                print(f"VERIFICATION FAILED: {u} and {v} interfere but both got {allocation[u]}")
                valid = False

    if valid:
        print("Verification: SUCCESS (No interfering variables share the same physical register)")

    print("Allocation Map: ", allocation)
    print("--- End Register Allocation ---")
