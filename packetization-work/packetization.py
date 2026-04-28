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
from collections import Counter
from ppci.arch.twig.reporter import write_packet_histogram_svg

def packetize_file(asm_file, max_packet_size=None):
    blocks = parse_asm(asm_file)

    # Use 32 registers for an apples-to-apples comparison with master's native scheduling 
    # (which assumes infinite/all 32 registers are available because it doesn't spill)
    allocate_registers_chaitin(blocks, num_registers=32)

    for b in blocks:
        b.build_ddg()

    counts = Counter()
    total_packets = 0
    total_instructions = 0

    for b in blocks:
        if not b.instructions:
            continue

        print(f"\n=== Basic Block: {b.name} ===")
        packets = greedy_packetize(b, max_packet_size)

        for p_idx, packet in enumerate(packets):
            print(f"  Packet {p_idx}:")
            packet_size = len(packet)
            counts[packet_size] += 1
            total_packets += 1
            total_instructions += packet_size
            for inst_idx in packet:
                inst = b.instructions[inst_idx]
                print(f"    [{inst_idx:2d}] {inst.original_text}")
    
    # Write the SVG
    basename = os.path.basename(asm_file).split('.')[0].replace("raw_", "")
    out_name = f"advay_{basename}.svg"
    write_packet_histogram_svg(out_name, dict(counts), total_packets, total_instructions)
    print(f"\nSaved histogram to {out_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python packetization.py <asm_file> [max_packet_size]")
        sys.exit(1)

    asm_file = sys.argv[1]
    max_packet_width = int(sys.argv[2]) if len(sys.argv) > 2 else None

    packetize_file(asm_file, max_packet_width)

