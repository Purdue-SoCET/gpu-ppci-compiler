import sys
from ddg import parse_asm
from reg_alloc import allocate_registers_chaitin


def greedy_packetize(block, max_packet_size=None):
    """
    greedily make packets from a basic block.
    """
    scheduled = []
    scheduled_set = set()
    packets = []

    total_insts = len(block.instructions)

    while len(scheduled_set) < total_insts:
        # get all instructions that have their dependencies met
        ready_list = block.get_ready_instructions(scheduled_set)

        # form a packet, up to max_packet_size
        if max_packet_size is not None and len(ready_list) > max_packet_size:
            packet = ready_list[:max_packet_size]
        else:
            packet = ready_list

        if not packet:
            # should never happen in a dag
            assert False
            break

        packets.append(packet)
        scheduled_set.update(packet)
        scheduled.extend(packet)

    return packets


import os


def packetize_text(asm_text: str, max_packet_size=None) -> str:
    from ddg import parse_asm_text

    blocks = parse_asm_text(asm_text)

    # Use 32 registers for an apples-to-apples comparison with master's native scheduling
    # (which assumes infinite/all 32 registers are available because it doesn't spill)
    allocate_registers_chaitin(blocks, num_registers=64)

    for b in blocks:
        b.build_ddg()

    import io

    f = io.StringIO()
    f.write("       .section code\n")

    for b in blocks:
        if not b.instructions:
            continue

        f.write(f"\n{b.name}:\n")
        f.write(f"; === Basic Block: {b.name} ===\n")
        packets = greedy_packetize(b, max_packet_size)

        for p_idx, packet in enumerate(packets):
            f.write(f";   Packet {p_idx}:\n")
            for inst_idx in packet:
                inst = b.instructions[inst_idx]
                f.write(f"    {inst.original_text}\n")

    return f.getvalue()


def packetize_file(asm_file, max_packet_size=None):
    with open(asm_file, "r") as f:
        asm_text = f.read()

    out_text = packetize_text(asm_text, max_packet_size)

    base_name = os.path.basename(asm_file)
    if base_name.startswith("raw_"):
        out_name = base_name.replace("raw_", "pkt_", 1)
    else:
        out_name = "pkt_" + base_name

    out_path = os.path.join(os.path.dirname(asm_file) or ".", out_name)

    with open(out_path, "w") as f:
        f.write(out_text)

    print(f"Success! Saved packetized assembly to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python packetization.py <asm_file> [max_packet_size]")
        sys.exit(1)

    asm_file = sys.argv[1]
    max_packet_width = int(sys.argv[2]) if len(sys.argv) > 2 else None

    packetize_file(asm_file, max_packet_width)
