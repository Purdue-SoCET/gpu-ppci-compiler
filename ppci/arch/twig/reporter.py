import math


def _compute_y_axis(max_count):
    if max_count <= 0:
        return 4, 1

    raw_step = max_count / 4
    magnitude = 10 ** int(math.floor(math.log10(raw_step)))
    normalized = raw_step / magnitude

    for candidate in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if normalized <= candidate:
            step = candidate * magnitude
            break

    if step >= 10:
        step = int(step)

    axis_max = step * 4
    return axis_max, step


def write_packet_histogram_svg(
    filename, counts, total_packets=0, total_instructions=0
):
    """Render packet size statistics as a dependency-free SVG image."""
    width = 900
    height = 560
    margin_left = 70
    margin_right = 30
    margin_top = 80
    margin_bottom = 90
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    max_packet_size = max(counts.keys(), default=1)
    actual_max_count = max(counts.values(), default=0)
    y_axis_max, y_tick_step = _compute_y_axis(actual_max_count)
    bar_gap = 12
    slot_width = chart_width / max_packet_size
    bar_width = max(12, min(64, slot_width - bar_gap))

    def sx(packet_size):
        return (
            margin_left
            + (packet_size - 1) * slot_width
            + (slot_width - bar_width) / 2
        )

    def sy(count):
        if y_axis_max <= 0:
            return margin_top + chart_height
        return margin_top + chart_height - (count / y_axis_max) * chart_height

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
        (
            f'<text x="{width / 2}" y="36" text-anchor="middle" '
            'font-family="sans-serif" font-size="24">'
            "Packet Size Histogram</text>"
        ),
        (
            f'<text x="{width / 2}" y="60" text-anchor="middle" '
            'font-family="sans-serif" font-size="13">'
            f"Total packets: {total_packets} | "
            f"Total instructions: {total_instructions}</text>"
        ),
        (
            f'<line x1="{margin_left}" y1="{margin_top + chart_height}" '
            f'x2="{margin_left + chart_width}" '
            f'y2="{margin_top + chart_height}" '
            'stroke="black" stroke-width="2"/>'
        ),
        (
            f'<line x1="{margin_left}" y1="{margin_top}" '
            f'x2="{margin_left}" y2="{margin_top + chart_height}" '
            'stroke="black" stroke-width="2"/>'
        ),
    ]

    for tick in range(5):
        count_value = y_tick_step * tick
        y = sy(count_value)
        lines.append(
            f'<line x1="{margin_left - 6}" y1="{y}" '
            f'x2="{margin_left}" y2="{y}" '
            'stroke="black" stroke-width="1"/>'
        )
        if tick > 0:
            lines.append(
                f'<line x1="{margin_left}" y1="{y}" '
                f'x2="{margin_left + chart_width}" y2="{y}" '
                'stroke="#dddddd" stroke-width="1"/>'
            )
        lines.append(
            f'<text x="{margin_left - 10}" y="{y + 4}" text-anchor="end" '
            f'font-family="sans-serif" font-size="12">{count_value}</text>'
        )

    for packet_size in range(1, max_packet_size + 1):
        count = counts.get(packet_size, 0)
        x = sx(packet_size)
        y = sy(count)
        bar_height = margin_top + chart_height - y
        lines.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
            'fill="#4e79a7" stroke="#2f4b6c" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{x + bar_width / 2}" '
            f'y="{margin_top + chart_height + 20}" '
            f'text-anchor="middle" font-family="sans-serif" '
            f'font-size="12">{packet_size}</text>'
        )
        if count:
            lines.append(
                f'<text x="{x + bar_width / 2}" '
                f'y="{max(y - 6, margin_top - 4)}" '
                f'text-anchor="middle" font-family="sans-serif" '
                f'font-size="12">{count}</text>'
            )

    lines.extend(
        [
            (
                f'<text x="{width / 2}" y="{height - 24}" '
                f'text-anchor="middle" '
                'font-family="sans-serif" font-size="14">'
                "Packet size (instructions per packet)</text>"
            ),
            (
                f'<text x="22" y="{margin_top + chart_height / 2}" '
                f'text-anchor="middle" '
                'font-family="sans-serif" font-size="14" '
                f'transform="rotate(-90 22 {margin_top + chart_height / 2})">'
                "Packet count</text>"
            ),
            "</svg>",
        ]
    )

    with open(filename, "w", encoding="utf-8") as out_file:
        out_file.write("\n".join(lines))
