import os
import struct
import asyncio

def ror32(x: int, r: int) -> int:
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def tea_decrypt_block(data: bytearray, key: list[int], rounds: int = 8) -> None:
    delta = 0x61C88647
    for offset in range(0, len(data), 8):
        v0, v1 = struct.unpack_from('<II', data, offset)
        sum_val = (-delta * rounds) & 0xFFFFFFFF
        for _ in range(rounds):
            v1 = (v1 - ((v0 + sum_val) ^ (key[3] + (v0 >> 5)) ^ (key[2] + (v0 << 4)))) & 0xFFFFFFFF
            new_sum = (sum_val + v1) & 0xFFFFFFFF
            sum_val = (sum_val + delta) & 0xFFFFFFFF
            v0 = (v0 - (new_sum ^ (key[0] + (v1 << 4)) ^ (key[1] + (v1 >> 5)))) & 0xFFFFFFFF
        struct.pack_into('<II', data, offset, v0, v1)

def patch_dff_header(dff_data: bytearray) -> bytearray:
    if len(dff_data) < 12:
        return dff_data
    real_size = len(dff_data) - 12
    return dff_data[:4] + struct.pack('<I', real_size) + dff_data[8:]

def clean_dff_data(dff_data: bytearray) -> bytearray:
    end = len(dff_data)
    while end > 0 and dff_data[end - 1] == 0:
        end -= 1
    return dff_data[:end]

def decrypt_mod_to_dff(mod_bytes: bytes) -> bytes:
    magic, length, num_blocks = struct.unpack_from('<III', mod_bytes, 0)
    if magic != 0xAB921033:
        raise ValueError("invalid .mod file")
    base_key = [0x6ED9EE7A, 0x930C666B, 0x930E166B, 0x4709EE79]
    key = [ror32(k ^ 0x12913AFB, 19) for k in base_key]

    data = bytearray(mod_bytes)
    offset = 28
    for _ in range(num_blocks):
        block = data[offset:offset + 0x800]
        tea_decrypt_block(block, key)
        data[offset:offset + 0x800] = block
        offset += 0x800

    actual_length = min(length, len(mod_bytes) - 28)
    dff = bytearray(data[28:28 + actual_length])
    dff = patch_dff_header(dff)
    dff = clean_dff_data(dff)
    return bytes(dff)

async def convert_one(mod_path: str, out_dir: str, log=None):
    name = os.path.splitext(os.path.basename(mod_path))[0]
    if log:
        log(f"[~] MOD → {name}.dff")

    os.makedirs(out_dir, exist_ok=True)
    try:
        mod_bytes = open(mod_path, 'rb').read()
        dff_bytes = decrypt_mod_to_dff(mod_bytes)
        out_path = os.path.join(out_dir, name + '.dff')
        with open(out_path, 'wb') as out_f:
            out_f.write(dff_bytes)
        print(f"[✓] {name}.dff")
    except Exception as e:
        print(f"[X] error {name}: {e}")

async def batch(mod_paths: list[str], out_dir: str, log=None):
    tasks = [convert_one(p, out_dir, log) for p in mod_paths]
    await asyncio.gather(*tasks)

def convert(mod_paths: list[str], out_dir: str, log=None):
    asyncio.run(batch(mod_paths, out_dir, log))
