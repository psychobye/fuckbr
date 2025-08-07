import argparse
import asyncio
import logging
import struct

from email import parser
from pathlib import Path
from typing import Optional, Tuple

parser = argparse.ArgumentParser(description="CLS")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the BTX")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def convert(in_path: str, out_dir: str) -> Optional[Tuple[str, str]]:
    if not Path(in_path).is_file():
        log.warning(f"[cls_convert] file not found: {in_path}")
        return None

    file_name = f"{Path(in_path).name}"
    log.info(f"[cls_convert] starting conversion for {file_name}")
    data = bytearray(open(in_path, 'rb').read())
    Path(out_dir).mkdir(parents=True, exist_ok=True)
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
        out = Path(out_dir) / fn
        if out.exists():
            out = Path(out_dir) / f"{name}_{cnt}.col"
        out.write_bytes(block)
        res.append(out)
        cnt += 1
        idx = pos + length

    log.info(f"[cls_convert] files saved in {out_dir}")
    return res

async def batch(input_dir: str, out_dir: str):
    cls_files = list(Path(input_dir).glob("*.cls"))
    if not cls_files:
        log.warning(f"[cls_convert] no CLS files found in {input_dir}")
        return
    tasks = [asyncio.to_thread(convert, str(p), out_dir) for p in cls_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
