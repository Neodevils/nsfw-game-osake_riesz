#!/usr/bin/env python3
import argparse
import struct
import sys
import zlib


def decompress(path):
    data = open(path, "rb").read()
    if data[:3] == b"CWS":
        return b"FWS" + data[3:8] + zlib.decompress(data[8:])
    if data[:3] == b"FWS":
        return data
    raise SystemExit(f"{path}: not an SWF")


def rect_bits_len(data, off):
    nbits = data[off] >> 3
    total_bits = 5 + nbits * 4
    return (total_bits + 7) // 8


TAG_NAMES = {
    1: "ShowFrame",
    2: "DefineShape",
    6: "DefineBits",
    9: "SetBackgroundColor",
    12: "DoAction",
    14: "DefineSound",
    18: "SoundStreamHead",
    19: "SoundStreamBlock",
    20: "DefineBitsLossless",
    21: "DefineBitsJPEG2",
    22: "DefineShape2",
    26: "PlaceObject2",
    28: "RemoveObject2",
    32: "DefineShape3",
    35: "DefineBitsJPEG3",
    36: "DefineBitsLossless2",
    39: "DefineSprite",
    43: "FrameLabel",
    46: "DefineMorphShape",
    48: "DefineFont2",
    56: "ExportAssets",
    57: "ImportAssets",
    59: "DoInitAction",
    60: "DefineVideoStream",
    62: "DefineFontInfo2",
    69: "FileAttributes",
    70: "PlaceObject3",
    73: "DefineFontAlignZones",
    75: "DefineFont3",
    76: "SymbolClass",
    77: "Metadata",
    82: "DoABC",
    83: "DefineShape4",
    84: "DefineMorphShape2",
    87: "DefineBinaryData",
    88: "DefineFontName",
    90: "DefineBitsJPEG4",
}


def c_string(buf, off):
    end = buf.find(b"\0", off)
    if end < 0:
        return "", len(buf)
    return buf[off:end].decode("utf-8", "replace"), end + 1


def iter_tags(data):
    off = 8 + rect_bits_len(data, 8) + 4
    while off + 2 <= len(data):
        raw = struct.unpack_from("<H", data, off)[0]
        off += 2
        code = raw >> 6
        length = raw & 0x3F
        if length == 0x3F:
            length = struct.unpack_from("<I", data, off)[0]
            off += 4
        body = data[off:off + length]
        yield code, body, off - (6 if (raw & 0x3F) == 0x3F else 2)
        off += length
        if code == 0:
            break


def inspect(path):
    data = decompress(path)
    print(f"{path}: version={data[3]} declared_len={struct.unpack_from('<I', data, 4)[0]} decompressed={len(data)}")
    counts = {}
    exports = []
    symbols = []
    labels = []
    images = []
    action_strings = []
    for code, body, pos in iter_tags(data):
        counts[code] = counts.get(code, 0) + 1
        if code == 56 and len(body) >= 2:
            count = struct.unpack_from("<H", body, 0)[0]
            p = 2
            for _ in range(count):
                if p + 2 > len(body):
                    break
                cid = struct.unpack_from("<H", body, p)[0]
                name, p = c_string(body, p + 2)
                exports.append((cid, name))
        elif code == 76 and len(body) >= 2:
            count = struct.unpack_from("<H", body, 0)[0]
            p = 2
            for _ in range(count):
                if p + 2 > len(body):
                    break
                cid = struct.unpack_from("<H", body, p)[0]
                name, p = c_string(body, p + 2)
                symbols.append((cid, name))
        elif code == 43:
            name, _ = c_string(body, 0)
            labels.append(name)
        elif code in (6, 20, 21, 35, 36, 90):
            cid = struct.unpack_from("<H", body, 0)[0] if len(body) >= 2 else -1
            images.append((code, cid, len(body)))
        elif code in (12, 59):
            start = 2 if code == 59 and len(body) > 2 else 0
            p = start
            while p < len(body):
                if body[p] == 0:
                    p += 1
                    continue
                q = p
                while q < len(body) and 32 <= body[q] <= 126:
                    q += 1
                if q - p >= 3:
                    s = body[p:q].decode("ascii", "replace")
                    action_strings.append(s)
                p = max(q + 1, p + 1)
    for code, count in sorted(counts.items()):
        print(f"  {code:3d} {TAG_NAMES.get(code, 'Tag'):<24} {count}")
    if labels:
        print("  labels:", ", ".join(labels[:40]))
    if exports:
        print("  exports:")
        for cid, name in exports[:80]:
            print(f"    {cid}: {name}")
    if symbols:
        print("  symbols:")
        for cid, name in symbols[:80]:
            print(f"    {cid}: {name}")
    if images:
        print("  image tags:")
        for code, cid, size in images[:80]:
            print(f"    {TAG_NAMES.get(code, code)} id={cid} bytes={size}")
    if action_strings:
        print("  action strings:")
        seen = set()
        for s in action_strings:
            if s in seen:
                continue
            seen.add(s)
            print(f"    {s}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    for path in args.paths:
        inspect(path)


if __name__ == "__main__":
    main()
