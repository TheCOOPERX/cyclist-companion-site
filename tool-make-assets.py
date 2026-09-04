#!/usr/bin/env python3
"""Build the site's image assets from the app repo's own captures.

Pure standard library — the site has no build step and no dependencies, and
this keeps it that way. Run it again whenever the screenshot or icon changes.

    python3 make_site_assets.py

Writes assets/shot-pressure.png (the on-page screenshot) and assets/og.png
(the 1200x630 social card).
"""

from __future__ import annotations

import pathlib
import struct
import zlib

SITE = pathlib.Path(__file__).resolve().parent
APP = pathlib.Path('/Users/cetadmin/cyclist_companion')

SHOT_SRC = APP / 'store/screenshots/6.9-inch/01-pressure.png'
ICON_SRC = SITE / 'assets/icon.png'

# Target brand tokens: Identity -> Deep. Phase C brings the app icon to these.
IDENTITY = (0xE8, 0x54, 0x1F)
DEEP = (0x9E, 0x2B, 0x07)
BEZEL = (0x14, 0x11, 0x10)


# --------------------------------------------------------------------------
# PNG decode. 8-bit non-interlaced, colour type 2 (RGB) or 6 (RGBA).
# --------------------------------------------------------------------------

def read_png(path: pathlib.Path) -> tuple[int, int, bytearray]:
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path}: not a PNG'
    pos, idat, w, h, chans = 8, bytearray(), 0, 0, 3
    while pos < len(data):
        (length,) = struct.unpack('>I', data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if tag == b'IHDR':
            w, h, depth, ctype, _, _, interlace = struct.unpack('>IIBBBBB', body)
            assert depth == 8 and interlace == 0, f'{path}: unsupported PNG'
            assert ctype in (2, 6), f'{path}: unsupported colour type {ctype}'
            chans = 3 if ctype == 2 else 4
        elif tag == b'IDAT':
            idat += body
        elif tag == b'IEND':
            break
        pos += 12 + length

    raw = zlib.decompress(bytes(idat))
    stride = w * chans
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ft == 1:
            for i in range(chans, stride):
                line[i] = (line[i] + line[i - chans]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = line[i - chans] if i >= chans else 0
                c = prev[i - chans] if i >= chans else 0
                b = prev[i]
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        prev = line
        # Drop alpha if present; these sources are all fully opaque.
        if chans == 3:
            out[y * w * 3:(y + 1) * w * 3] = line
        else:
            row = out
            o = y * w * 3
            for x in range(w):
                row[o + x * 3:o + x * 3 + 3] = line[x * 4:x * 4 + 3]
    return w, h, out


# --------------------------------------------------------------------------
# PNG encode. Per-row filter choice, which matters a lot for flat UI art.
# --------------------------------------------------------------------------

def write_png(path: pathlib.Path, w: int, h: int, rgb: bytearray) -> None:
    stride = w * 3
    raw = bytearray()
    prev = bytearray(stride)
    for y in range(h):
        line = rgb[y * stride:(y + 1) * stride]
        none = line
        sub = bytearray(stride)
        up = bytearray(stride)
        for i in range(stride):
            a = line[i - 3] if i >= 3 else 0
            sub[i] = (line[i] - a) & 0xFF
            up[i] = (line[i] - prev[i]) & 0xFF

        def cost(b: bytearray) -> int:
            return sum(v if v < 128 else 256 - v for v in b)

        best = min(((0, none), (1, sub), (2, up)), key=lambda t: cost(t[1]))
        raw.append(best[0])
        raw += best[1]
        prev = line

    def chunk(tag: bytes, body: bytes) -> bytes:
        return (struct.pack('>I', len(body)) + tag + body
                + struct.pack('>I', zlib.crc32(tag + body) & 0xFFFFFFFF))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    path.write_bytes(png)


def scale(sw: int, sh: int, src: bytearray, dw: int, dh: int) -> bytearray:
    """Box-filter resample. Area-averaging keeps downscaled UI text readable."""
    dst = bytearray(dw * dh * 3)
    for dy in range(dh):
        y0, y1 = dy * sh // dh, max(dy * sh // dh + 1, (dy + 1) * sh // dh)
        for dx in range(dw):
            x0, x1 = dx * sw // dw, max(dx * sw // dw + 1, (dx + 1) * sw // dw)
            r = g = b = n = 0
            for y in range(y0, y1):
                base = y * sw * 3
                for x in range(x0, x1):
                    o = base + x * 3
                    r += src[o]; g += src[o + 1]; b += src[o + 2]
                    n += 1
            o = (dy * dw + dx) * 3
            dst[o] = r // n; dst[o + 1] = g // n; dst[o + 2] = b // n
    return dst


def blit(dst: bytearray, dw: int, dh: int, src: bytearray, sw: int, sh: int,
         ox: int, oy: int, radius: int = 0) -> None:
    """Paste src at (ox, oy), clipped to the canvas, with optional rounded corners."""
    for y in range(sh):
        ty = oy + y
        if not (0 <= ty < dh):
            continue
        for x in range(sw):
            tx = ox + x
            if not (0 <= tx < dw):
                continue
            if radius:
                cx = radius - x if x < radius else (x - (sw - radius - 1) if x > sw - radius - 1 else 0)
                cy = radius - y if y < radius else (y - (sh - radius - 1) if y > sh - radius - 1 else 0)
                if cx and cy and cx * cx + cy * cy > radius * radius:
                    continue
            s, d = (y * sw + x) * 3, (ty * dw + tx) * 3
            dst[d:d + 3] = src[s:s + 3]


def rounded_rect(dst: bytearray, dw: int, dh: int, x0: int, y0: int,
                 w: int, h: int, colour: tuple, radius: int) -> None:
    for y in range(h):
        ty = y0 + y
        if not (0 <= ty < dh):
            continue
        for x in range(w):
            tx = x0 + x
            if not (0 <= tx < dw):
                continue
            cx = radius - x if x < radius else (x - (w - radius - 1) if x > w - radius - 1 else 0)
            cy = radius - y if y < radius else (y - (h - radius - 1) if y > h - radius - 1 else 0)
            if cx and cy and cx * cx + cy * cy > radius * radius:
                continue
            d = (ty * dw + tx) * 3
            dst[d] = colour[0]; dst[d + 1] = colour[1]; dst[d + 2] = colour[2]


def main() -> None:
    print('reading', SHOT_SRC.name)
    sw, sh, shot = read_png(SHOT_SRC)

    # 1. On-page screenshot: 2x asset for a ~320px display width.
    dw = 640
    dh = round(sh * dw / sw)
    out = SITE / 'assets/shot-pressure.png'
    write_png(out, dw, dh, scale(sw, sh, shot, dw, dh))
    print(f'wrote {out.name}  {dw}x{dh}  {out.stat().st_size // 1024} KB')

    # 2. Social card: 1200x630, brand gradient, app icon, phone bleeding off
    #    the bottom-right so the card reads as a product shot, not a logo.
    W, H = 1200, 630
    card = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            t = (x / W + y / H) * 0.5
            o = (y * W + x) * 3
            card[o] = round(IDENTITY[0] + (DEEP[0] - IDENTITY[0]) * t)
            card[o + 1] = round(IDENTITY[1] + (DEEP[1] - IDENTITY[1]) * t)
            card[o + 2] = round(IDENTITY[2] + (DEEP[2] - IDENTITY[2]) * t)

    screen_h = 640
    screen_w = round(sw * screen_h / sh)
    px, py = 742, 96
    pad = 12
    rounded_rect(card, W, H, px - pad, py - pad,
                 screen_w + pad * 2, screen_h + pad * 2, BEZEL, 46)
    blit(card, W, H, scale(sw, sh, shot, screen_w, screen_h),
         screen_w, screen_h, px, py, radius=36)

    iw, ih, icon = read_png(ICON_SRC)
    side = 300
    blit(card, W, H, scale(iw, ih, icon, side, side), side, side,
         168, (H - side) // 2, radius=68)

    out = SITE / 'assets/og.png'
    write_png(out, W, H, card)
    print(f'wrote {out.name}  {W}x{H}  {out.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
