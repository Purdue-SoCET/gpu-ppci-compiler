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
    width = 640
    height = 340

    margin_left = 50
    margin_right = 14
    margin_top = 52
    margin_bottom = 42

    title_font = 18
    subtitle_font = 11
    tick_font = 10
    value_font = 10
    axis_font = 11

    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    max_packet_size = max(counts.keys(), default=1)
    actual_max_count = max(counts.values(), default=0)
    y_axis_max, y_tick_step = _compute_y_axis(actual_max_count)

    slot_width = chart_width / max_packet_size

    # Use a percentage of each slot instead of a fixed hard cap.
    if max_packet_size <= 8:
        bar_width = slot_width * 0.78
    elif max_packet_size <= 16:
        bar_width = slot_width * 0.72
    else:
        bar_width = slot_width * 0.64

    bar_width = max(10, min(bar_width, slot_width - 4))

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
            f'<text x="{width / 2}" y="24" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{title_font}">Packet Size Histogram</text>'
        ),
        (
            f'<text x="{width / 2}" y="40" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{subtitle_font}">'
            f'Total packets: {total_packets} | Total instructions: {total_instructions}'
            '</text>'
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
            f'<line x1="{margin_left - 5}" y1="{y}" x2="{margin_left}" y2="{y}" '
            'stroke="black" stroke-width="1"/>'
        )
        if tick > 0:
            lines.append(
                f'<line x1="{margin_left}" y1="{y}" '
                f'x2="{margin_left + chart_width}" y2="{y}" '
                'stroke="#dddddd" stroke-width="1"/>'
            )
        lines.append(
            f'<text x="{margin_left - 8}" y="{y + 3}" text-anchor="end" '
            f'font-family="sans-serif" font-size="{tick_font}">{count_value}</text>'
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
            f'<text x="{x + bar_width / 2}" y="{margin_top + chart_height + 16}" '
            f'text-anchor="middle" font-family="sans-serif" font-size="{tick_font}">{packet_size}</text>'
        )

        if count:
            lines.append(
                f'<text x="{x + bar_width / 2}" y="{max(y - 4, margin_top - 2)}" '
                f'text-anchor="middle" font-family="sans-serif" font-size="{value_font}">{count}</text>'
            )

    lines.extend([
        (
            f'<text x="{width / 2}" y="{height - 14}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{axis_font}">Packet size</text>'
        ),
        (
            f'<text x="18" y="{margin_top + chart_height / 2}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{axis_font}" '
            f'transform="rotate(-90 18 {margin_top + chart_height / 2})">Packet count</text>'
        ),
        '</svg>',
    ])

    with open(filename, "w", encoding="utf-8") as out_file:
        out_file.write("\n".join(lines))
