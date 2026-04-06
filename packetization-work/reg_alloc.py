import sys
import re

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

def color_graph(adj_list, num_registers):
    """
    Chaitin's
    Colors from x1 to x{num_registers-1}. x0 is hardwired.
    """
    colors_available = [f"x{i}" for i in range(1, num_registers)]
    num_colors = len(colors_available)

    stack = []
    spilled_nodes = []
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
                allocation[node] = possible_colors[0] # Fallback
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


spill_offset = 1024

def insert_spill_code(blocks, spilled_nodes):
    global spill_offset
    from ddg import Instruction
    
    spill_counter = 0
    spill_offsets = {}
    for node in spilled_nodes:
        if node not in spill_offsets:
            spill_offsets[node] = spill_offset
            spill_offset += 4

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
                inst.original_text = re.sub(rf"\b{s}\b", temp_reg, inst.original_text)
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
                inst.original_text = re.sub(rf"\b{inst.dest}\b", temp_reg, inst.original_text)
                inst.dest = temp_reg

                # Create a store instruction AFTER the def
                store_text = f"sw {temp_reg}, {offset}(x0)"
                store_idx = len(new_instructions)
                store_inst = Instruction(store_idx, store_text)
                new_instructions.append(store_inst)
                
        b.instructions = new_instructions

def allocate_registers_chaitin(blocks, num_registers=32):
    print("\n--- Live Range Splitting Phase ---")
    split_live_ranges(blocks)

    max_iter = 10
    iteration = 0
    while True:
        compute_liveness(blocks)
        adj_list = build_interference_graph(blocks)

        print(f"--- Register Allocation Phase (Iter {iteration}) ---")
        print(f"Extracted {len(adj_list)} Virtual Variables")

        allocation, spilled_nodes = color_graph(adj_list, num_registers)
        
        if not spilled_nodes:
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
            break
        else:
            print(f"Spilling nodes: {spilled_nodes}")
            insert_spill_code(blocks, spilled_nodes)
            iteration += 1
            if iteration > max_iter:
                raise Exception("Exceeded max iterations for spilling. Graph won't color.")
