import argparse
import asyncio
import logging
import struct

from pathlib import Path
from typing import Optional, Tuple

from config import (
    SEMAPHORE
)

parser = argparse.ArgumentParser(description="CLS")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the CLS")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def convert(in_path: str, out_dir: str) -> Optional[Tuple[str, str]]:
    data = bytearray(open(in_path, "rb").read())
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    file_name = f"{Path(in_path).name}"
    log.info(f"[cls_convert] starting conversion for {file_name}")

    idx = 0
    cnt = 0
    blocks = []
    while True:
        pos = data.find(b"CLST", idx)
        if pos < 0:
            break
        length_field = struct.unpack_from("<I", data, pos + 4)[0]
        candidate_end = pos + 8 + length_field
        if candidate_end > len(data):
            candidate_end = len(data)

        block = bytearray(data[pos:candidate_end])
        block[0:4] = b"COL3"

        declared = len(block) - 8
        if declared < 0:
            declared = 0
        struct.pack_into("<I", block, 4, declared)

        while len(block) % 4 != 0:
            block += b"\x00"

        declared = len(block) - 8
        struct.pack_into("<I", block, 4, declared)

        # debug chunks
        # log.info(f"[cls_convert] pos={pos} length_field={length_field} block_len={len(block)} declared={declared}")
        blocks.append(block)

        cnt += 1
        idx = pos + 8 + length_field

    if not blocks:
        log.error(f"[cls_convert] no clst blocks in {in_path}")
        return None

    out_name = Path(in_path).with_suffix(".col").name
    out_path = Path(out_dir) / out_name

    if out_path.exists():
        out_path = Path(out_dir) / f"{Path(in_path).stem}_{int(Path(out_dir).glob('*.col').__length_hint__())}.col"

    merged = bytearray()
    for b in blocks:
        merged += b

    out_path.write_bytes(merged)
    log.info(f"[cls_convert] saved merged {out_path} with {len(blocks)} blocks, total {len(merged)} bytes")
    return [out_path]

async def semaphore(cls_path, out_dir):
    async with SEMAPHORE:
        return await convert(cls_path, out_dir)

async def batch(input_dir: str, out_dir: str):
    cls_files = list(Path(input_dir).glob("*.cls"))
    if not cls_files:
        log.warning(f"[cls_convert] no CLS files found in {input_dir}")
        return
    tasks = [semaphore(str(p), out_dir) for p in cls_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
