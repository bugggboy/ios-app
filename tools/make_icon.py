#!/usr/bin/env python3
"""生成一个占位 App 图标（1024x1024 PNG），只用标准库，Windows / macOS 都能跑。

用法：
    python tools/make_icon.py
    python tools/make_icon.py --bg 47,109,17

真做 App 的时候把这个文件换成自己的图标即可（直接覆盖 icon-1024.png）。
"""
import argparse
import os
import struct
import zlib

SIZE = 1024
DEFAULT_BG = (79, 70, 229)      # indigo
FG = (255, 255, 255)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge1 <= edge0:
        return 0.0 if x < edge0 else 1.0
    t = (x - edge0) / (edge1 - edge0)
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return t * t * (3.0 - 2.0 * t)


def coverage(x: int, y: int) -> float:
    """圆环 + 中心圆点的平滑覆盖率，0..1。"""
    cx = cy = SIZE / 2.0
    r = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    aa = 1.5
    ring = smoothstep(250 - aa, 250 + aa, r) * (1.0 - smoothstep(330 - aa, 330 + aa, r))
    dot = 1.0 - smoothstep(70 - aa, 70 + aa, r)
    return max(ring, dot)


def build_png(bg):
    rows = []
    for y in range(SIZE):
        row = bytearray()
        row.append(0)  # filter type: none
        for x in range(SIZE):
            c = coverage(x, y)
            row.append(int(round(bg[0] * (1 - c) + FG[0] * c)))
            row.append(int(round(bg[1] * (1 - c) + FG[1] * c)))
            row.append(int(round(bg[2] * (1 - c) + FG[2] * c)))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bg", default="79,70,229", help="背景色，形如 79,70,229")
    parser.add_argument(
        "--out",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "Sources", "Assets.xcassets", "AppIcon.appiconset", "icon-1024.png",
        ),
    )
    args = parser.parse_args()
    bg = tuple(int(v) for v in args.bg.split(","))
    if len(bg) != 3:
        raise SystemExit("--bg 需要三个 0-255 的数字")

    data = build_png(bg)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(data)
    print(f"已写入 {args.out}（{len(data) / 1024:.1f} KB）")


if __name__ == "__main__":
    main()
