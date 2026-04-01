import sys
from collections import defaultdict


class Instruction:
    def __init__(self, id, text):
        self.id = id
        self.original_text = text.strip()
        self.opcode = None
        self.dest = None
        self.srcs = set()
        self.is_mem_read = False
        self.is_mem_write = False
        self.is_branch = False
        self.branch_target = None
        self.parse()

    def parse(self):
        clean_text = (
            self.original_text.replace(",", " ")
            .replace("(", " ")
            .replace(")", " ")
        )
        parts = clean_text.split()
        if not parts:
            return

        self.opcode = parts[0]

        if self.opcode in ["lui", "lmi", "lli"]:
            if len(parts) >= 2:
                self.dest = parts[1]
        elif self.opcode in [
            "add",
            "sub",
            "mul",
            "div",
            "mulf",
            "addf",
            "subf",
            "divf",
            "and",
            "or",
            "xor",
            "sll",
            "srl",
            "sra",
        ]:
            if len(parts) >= 4:
                self.dest = parts[1]
                self.srcs.update([parts[2], parts[3]])
        elif self.opcode in [
            "addi",
            "subi",
            "andi",
            "ori",
            "xori",
            "slli",
            "srli",
            "srai",
        ]:
            if len(parts) >= 3:
                self.dest = parts[1]
                self.srcs.add(parts[2])
        elif self.opcode == "sw":
            self.is_mem_write = True
            if len(parts) >= 4:
                # typically `sw src offset base`
                self.srcs.update([parts[1], parts[3]])
        elif self.opcode == "lw":
            self.is_mem_read = True
            if len(parts) >= 4:
                self.dest = parts[1]
                self.srcs.add(parts[3])
        elif self.opcode in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
            self.is_branch = True
            if len(parts) >= 4:
                self.branch_target = parts[1]
                self.srcs.update([parts[2], parts[3]])
        elif self.opcode in ["jal"]:
            self.is_branch = True
            if len(parts) >= 3:
                self.dest = parts[1]
                self.branch_target = parts[2]
        elif self.opcode in ["jalr"]:
            self.is_branch = True
            if len(parts) >= 3:
                self.dest = parts[1]
                self.srcs.add(parts[2])
        elif self.opcode == "csrr":
            if len(parts) >= 3:
                self.dest = parts[1]
                # CSR indices are not general purpose registers

        # register x0 is hardwired to 0, no data dependencies on it
        if self.dest == "x0":
            self.dest = None
        self.srcs.discard("x0")


class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.instructions = []
        # edge structure: node -> list( (dependent_node, type) )
        self.forward_edges = defaultdict(list)
        self.backward_edges = defaultdict(list)

        # CFG Edges
        self.predecessors = []
        self.successors = []

    def add_instruction(self, inst):
        self.instructions.append(inst)

    def add_edge(self, src_idx, dst_idx, dep_type="RAW"):
        self.forward_edges[src_idx].append((dst_idx, dep_type))
        self.backward_edges[dst_idx].append((src_idx, dep_type))

    def build_ddg(self):
        self.forward_edges.clear()
        self.backward_edges.clear()

        last_writer = {}
        last_readers = defaultdict(list)

        last_mem_write = None
        last_mem_reads = []

        for i, inst in enumerate(self.instructions):
            # RAW edges (reads from last writer)
            for src in inst.srcs:
                if src in last_writer:
                    self.add_edge(last_writer[src], i, f"RAW({src})")
                last_readers[src].append(i)

            # WAW and WAR edges
            if inst.dest:
                if inst.dest in last_writer and last_writer[inst.dest] != i:
                    self.add_edge(
                        last_writer[inst.dest], i, f"WAW({inst.dest})"
                    )
                for reader in last_readers[inst.dest]:
                    # WAR applies if a reader read the state before this write
                    if reader != i:
                        self.add_edge(reader, i, f"WAR({inst.dest})")

                last_writer[inst.dest] = i
                last_readers[
                    inst.dest
                ] = []  # clear readers for this reg after a write

            # memory dependencies (for now we treat memory as a single resource)
            if inst.is_mem_read:
                if last_mem_write is not None:
                    self.add_edge(last_mem_write, i, "RAW(MEM)")
                last_mem_reads.append(i)

            if inst.is_mem_write:
                if last_mem_write is not None:
                    self.add_edge(last_mem_write, i, "WAW(MEM)")
                for reader in last_mem_reads:
                    self.add_edge(reader, i, "WAR(MEM)")
                last_mem_write = i
                last_mem_reads = []

    def get_ready_instructions(self, scheduled_instructions):
        """
        Helper for greedy packetization.
        Given a list of scheduled instruction indices, returns
        the indices of instructions that are ready to be scheduled.
        """
        ready = []
        scheduled_set = set(scheduled_instructions)
        for i in range(len(self.instructions)):
            if i in scheduled_set:
                continue

            all_met = True
            for dep, dtype in self.backward_edges[i]:
                if dep not in scheduled_set:
                    all_met = False
                    break

            if all_met:
                ready.append(i)
        return ready


def parse_asm(file_path):
    blocks = []
    current_block = None
    in_code_section = False

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("section code"):
                in_code_section = True
                continue
            elif line.startswith("section data"):
                in_code_section = False
                continue

            if not in_code_section:
                continue

            if (
                line.startswith("global ")
                or line.startswith("type ")
                or line.startswith(".align")
            ):
                continue

            if line.endswith(":"):
                label = line[:-1]
                current_block = BasicBlock(label)
                blocks.append(current_block)
                continue

            if current_block is None:
                current_block = BasicBlock("entry")
                blocks.append(current_block)

            inst_idx = len(current_block.instructions)
            inst = Instruction(inst_idx, line)
            current_block.add_instruction(inst)

    for b in blocks:
        b.build_ddg()

    build_cfg(blocks)

    return blocks

def build_cfg(blocks):
    block_map = {b.name: b for b in blocks}

    for i, b in enumerate(blocks):
        # check the last few instructions for branch/jump
        ends_with_unconditional = False

        for inst in reversed(b.instructions):
            if inst.is_branch and inst.branch_target:
                target_name = None

                if inst.branch_target in block_map:
                    target_name = inst.branch_target
                else:
                    for name in block_map.keys():
                        if name.endswith(inst.branch_target) or name.endswith("block" + inst.branch_target):
                            target_name = name
                            break

                if target_name:
                    target_block = block_map[target_name]
                    if target_block not in b.successors:
                        b.successors.append(target_block)
                        target_block.predecessors.append(b)

                if inst.opcode == "jal":
                    ends_with_unconditional = True
                    break
            elif inst.opcode == "jalr":
                ends_with_unconditional = True
                break

        if not ends_with_unconditional and i + 1 < len(blocks):
            next_block = blocks[i+1]
            if next_block not in b.successors:
                b.successors.append(next_block)
                next_block.predecessors.append(b)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ddg.py <asm_file>")
        sys.exit(1)

    blocks = parse_asm(sys.argv[1])
    for b in blocks:
        if not b.instructions:
            continue
        print(f"\n=== Basic Block: {b.name} ===")
        for i, inst in enumerate(b.instructions):
            deps = b.backward_edges[i]
            dep_str = ", ".join([f"[{src}]: {dtype}" for src, dtype in deps])
            if not dep_str:
                dep_str = "None"
            print(
                f"  {i:2d}: {inst.original_text:30} -> Depends on: {dep_str}"
            )

        ready_init = b.get_ready_instructions([])
        print(f"  -- Ready to schedule (Level 0): {ready_init}")
