import struct
import os

input_dir = 'cls'
output_dir = 'col'

def split_cls_to_cols(input_path, output_dir):
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    os.makedirs(output_dir, exist_ok=True)
    i = 0
    part = 0

    while True:
        idx = data.find(b'CLST', i)
        if idx == -1:
            break

        old_len = struct.unpack_from('<I', data, idx+4)[0]
        block = data[idx:idx+old_len]

        # gta sa format
        block[0:4] = b'COL3'
        struct.pack_into('<I', block, 4, old_len - 8)

        # name parsing
        raw_name = block[8:8+22]
        name = raw_name.split(b'\x00', 1)[0].decode('ascii', errors='ignore') or f'part{part}'
        filename = f"{name}.col"
        out_path = os.path.join(output_dir, filename)

        if os.path.exists(out_path):
            filename = f"{name}_{part}.col"
            out_path = os.path.join(output_dir, filename)

        with open(out_path, 'wb') as out:
            out.write(block)
        print(f"[+] saved {out_path}")

        part += 1
        i = idx + old_len

if __name__ == '__main__':
    for fname in os.listdir(input_dir):
        if fname.lower().endswith('.cls'):
            in_path = os.path.join(input_dir, fname)
            split_cls_to_cols(in_path, output_dir)
