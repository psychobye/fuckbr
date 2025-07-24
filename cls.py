import os
import sys
import struct

def split_cls_file(in_path: str, out_dir: str) -> list:
    if not os.path.isfile(in_path):
        raise FileNotFoundError(in_path)
    data = bytearray(open(in_path, 'rb').read())
    os.makedirs(out_dir, exist_ok=True)
    res = []
    idx = 0
    cnt = 0
    while True:
        pos = data.find(b'CLST', idx)
        if pos < 0: break
        length = struct.unpack_from('<I', data, pos+4)[0]
        block = data[pos:pos+length]
        block[0:4] = b'COL3'
        struct.pack_into('<I', block, 4, length-8)
        raw = block[8:30]
        name = raw.split(b'\x00',1)[0].decode('ascii',errors='ignore') or f"part{cnt}"
        fn = f"{name}.col"
        out = os.path.join(out_dir, fn)
        if os.path.exists(out):
            out = os.path.join(out_dir, f"{name}_{cnt}.col")
        open(out, 'wb').write(block)
        res.append(out)
        cnt += 1
        idx = pos + length
    return res

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser("CLS→COL")
    p.add_argument("inputs", nargs='+', help=".cls files")
    p.add_argument("--out", help="out dir", default="col")
    args = p.parse_args()
    for f in args.inputs:
        try:
            lst = split_cls_file(f, args.out)
            for x in lst: print("[+]", x)
        except Exception as e:
            print("[!]", f, e)
