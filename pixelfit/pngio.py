"""Minimal PNG codec, stdlib only.

Scope: 8-bit, non-interlaced, color types 0 (gray), 2 (RGB), 6 (RGBA).
Anything else is rejected loudly rather than misread.
"""
import struct
import zlib

SIG = b"\x89PNG\r\n\x1a\n"
_CHANNELS = {0: 1, 2: 3, 6: 4}


def read_png(path):
    """Return (width, height, channels, data) with data as flat bytes."""
    with open(path, "rb") as fh:
        data = fh.read()
    if not data.startswith(SIG):
        raise ValueError(f"{path}: not a PNG file")
    pos = 8
    idat = []
    ihdr = None
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        pos += 8
        payload = data[pos:pos + length]
        pos += length + 4  # skip CRC
        if ctype == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", payload)
        elif ctype == b"IDAT":
            idat.append(payload)
        elif ctype == b"IEND":
            break
    if ihdr is None:
        raise ValueError(f"{path}: missing IHDR")
    w, h, depth, color, _comp, _filt, interlace = ihdr
    if depth != 8 or color not in _CHANNELS or interlace != 0:
        raise ValueError(
            f"{path}: unsupported PNG (depth={depth}, colortype={color}, "
            f"interlace={interlace}); supported: 8-bit non-interlaced "
            f"gray/RGB/RGBA")
    c = _CHANNELS[color]
    raw = zlib.decompress(b"".join(idat))
    stride = w * c
    if len(raw) != (stride + 1) * h:
        raise ValueError(f"{path}: corrupt PNG stream")
    out = bytearray(stride * h)
    prior = bytearray(stride)
    p = 0
    for y in range(h):
        ftype = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ftype == 1:
            for i in range(c, stride):
                line[i] = (line[i] + line[i - c]) & 255
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prior[i]) & 255
        elif ftype == 3:
            for i in range(stride):
                left = line[i - c] if i >= c else 0
                line[i] = (line[i] + ((left + prior[i]) >> 1)) & 255
        elif ftype == 4:
            for i in range(stride):
                a = line[i - c] if i >= c else 0
                b = prior[i]
                d = prior[i - c] if i >= c else 0
                pa, pb, pd = abs(b - d), abs(a - d), abs(a + b - 2 * d)
                pred = a if pa <= pb and pa <= pd else (b if pb <= pd else d)
                line[i] = (line[i] + pred) & 255
        elif ftype != 0:
            raise ValueError(f"{path}: bad filter type {ftype}")
        out[y * stride:(y + 1) * stride] = line
        prior = line
    return w, h, c, out


def write_png(path, w, h, c, data):
    """Write flat bytes as an 8-bit PNG. No filtering (type 0 rows)."""
    color = {1: 0, 3: 2, 4: 6}[c]
    stride = w * c
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += data[y * stride:(y + 1) * stride]

    def chunk(ctype, payload):
        return (struct.pack(">I", len(payload)) + ctype + payload
                + struct.pack(">I", zlib.crc32(ctype + payload)))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, color, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(SIG)
        fh.write(chunk(b"IHDR", ihdr))
        fh.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        fh.write(chunk(b"IEND", b""))
