import json
import binascii
from pathlib import Path
from typing import Iterable, Tuple, Optional

from ppci.binutils.linker import link


def link_oj(
    input_oj: str = "prog.oj",
    layout_file: str = "layout",
    entry: str = "main",
    output_oj: str = "prog_linked.oj",
) -> str:
    """
    Final link + apply layout (partial_link=False) and write linked .oj.
    This avoids ppci-ld's ELF emission path (which fails for custom arch like 'twig').
    """
    obj = link(
        objects=[input_oj],
        layout=layout_file,      # PPCI layout DSL file
        partial_link=False,      # must be False to apply layout/images
        entry=entry,
    )

    out_path = Path(output_oj)
    with out_path.open("w", encoding="utf-8") as f:
        obj.save(f)

    print(f"[OK] Wrote linked object: {out_path}")
    return str(out_path)


def _hexlist_to_bytes(x) -> bytes:
    # x can be list[str] or str
    if isinstance(x, list):
        x = "".join(x)
    if not x:
        return b""
    return binascii.unhexlify(x)


def oj_to_bin(
    linked_oj: str = "prog_linked.oj",
    output_bin: str = "prog.bin",
    image_name: str = "rom",
) -> Tuple[str, int, int, Iterable[str]]:
    """
    Build a raw binary from a linked .oj.
    Supports your observed image shape:
        images: [{name, address, sections: ['code','data',...]}]
    and section bytes stored in top-level sections[].data.

    Returns: (bin_path, load_address, size_bytes, section_order)
    """
    with Path(linked_oj).open("r", encoding="utf-8") as f:
        oj = json.load(f)

    images = oj.get("images", [])
    try:
        img = next(i for i in images if i.get("name") == image_name)
    except StopIteration:
        raise RuntimeError(f"Image '{image_name}' not found in {linked_oj}. images={images}")

    base = int(img.get("address", "0x0"), 16)

    sec_by_name = {s["name"]: s for s in oj.get("sections", []) if "name" in s}

    order = img.get("sections", [])
    if not isinstance(order, list) or not order:
        raise RuntimeError(f"Image '{image_name}' has no section list; got: {order}")

    pieces = []
    max_end = 0
    for name in order:
        s = sec_by_name.get(name)
        if s is None:
            raise RuntimeError(f"Image '{image_name}' references missing section '{name}'")

        addr = int(s.get("address", "0x0"), 16) - base
        b = _hexlist_to_bytes(s.get("data", ""))
        pieces.append((addr, b, name))
        max_end = max(max_end, addr + len(b))

    buf = bytearray(max_end)
    for addr, b, name in pieces:
        buf[addr:addr + len(b)] = b

    raw = bytes(buf)
    out_path = Path(output_bin)
    out_path.write_bytes(raw)

    print(f"[OK] Wrote binary: {out_path} ({len(raw)} bytes), load_address=0x{base:x}, sections={order}")
    return str(out_path), base, len(raw), order


def build_all(
    input_oj: str = "prog.oj",
    layout_file: str = "layout",
    entry: str = "main",
    linked_oj: str = "prog_linked.oj",
    output_bin: str = "prog.bin",
    image_name: str = "rom",
) -> None:
    """
    Convenience: link -> linked .oj -> raw binary.
    """
    link_oj(input_oj=input_oj, layout_file=layout_file, entry=entry, output_oj=linked_oj)
    oj_to_bin(linked_oj=linked_oj, output_bin=output_bin, image_name=image_name)


if __name__ == "__main__":
    build_all()