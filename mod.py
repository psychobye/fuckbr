import os
import sys
import struct

def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def tea_decrypt_block(data: bytearray, key: list, rounds=8):
    delta = 0x61C88647
    for off in range(0, len(data), 8):
        v0, v1 = struct.unpack_from('<II', data, off)
        s = (-delta * rounds) & 0xFFFFFFFF
        for _ in range(rounds):
            v1 = (v1 - ((v0 + s) ^ (key[3] + (v0 >> 5)) ^ (key[2] + (v0 << 4)))) & 0xFFFFFFFF
            s = (s + v1) & 0xFFFFFFFF
            v0 = (v0 - (s ^ (key[0] + (v1 << 4)) ^ (key[1] + (v1 >> 5)))) & 0xFFFFFFFF
        struct.pack_into('<II', data, off, v0, v1)

def decrypt_mod(filepath: str) -> bytes:
    data = bytearray(open(filepath, 'rb').read())
    magic, length, blocks = struct.unpack_from('<III', data, 0)
    if magic != 0xAB921033:
        raise ValueError("not .mod")
    base = [0x6ED9EE7A,0x930C666B,0x930E166B,0x4709EE79]
    key = [ror32(k ^ 0x12913AFB, 19) for k in base]
    offset = 28
    for _ in range(blocks):
        chunk = data[offset:offset+0x800]
        tea_decrypt_block(chunk, key)
        data[offset:offset+0x800] = chunk
        offset += 0x800
    body = data[28:28+min(length, len(data)-28)]
    # clean header
    body = body[:4] + struct.pack('<I', len(body)-12) + body[8:]
    # trim zeros
    return body.rstrip(b'\x00')

def convert_mods(file_list: list, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    for f in file_list:
        try:
            out = os.path.join(out_dir, os.path.basename(f).replace('.mod','.dff'))
            open(out, 'wb').write(decrypt_mod(f))
            print("[✓]", out)
        except Exception as e:
            print("[X]", f, e)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser("MOD→DFF")
    p.add_argument("inputs", nargs='+', help=".mod files")
    p.add_argument("--out", help="out dir", default="dff")
    args = p.parse_args()
    convert_mods(args.inputs, args.out)
