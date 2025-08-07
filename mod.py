import argparse
import logging
import struct
import asyncio

from pathlib import Path

parser = argparse.ArgumentParser(description="MOD")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the MOD")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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
        log.error("[mod_convert] invalid .mod file")
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

async def convert(mod_path: str, out_dir: str):
    name = Path(mod_path).stem
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    try:
        mod_bytes = open(mod_path, 'rb').read()
        dff_bytes = decrypt_mod_to_dff(mod_bytes)
        out_path = Path(out_dir) / f"{name}.dff"
        with open(out_path, 'wb') as out_f:
            out_f.write(dff_bytes)
        log.info(f"[✓] {name}.dff")
    except Exception as e:
        log.error(f"[X] error {name}: {e}")

async def batch(input_dir: str, out_dir: str):
    files = list(Path(input_dir).glob("*.mod"))
    if not files:
        log.warning(f"[mod_convert] no MOD files found in {input_dir}")
        return
    tasks = [convert(str(p), out_dir) for p in files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
