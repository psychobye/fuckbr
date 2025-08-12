import argparse
import asyncio
import logging

from pathlib import Path
from typing import Optional, Tuple

from config import (
    SEMAPHORE
)

parser = argparse.ArgumentParser(description="ANI")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the ANI")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def convert(in_path: str, out_dir: str) -> Optional[Tuple[str, str]]:
    in_path_obj = Path(in_path)
    if not Path(in_path).is_file():
        log.warning(f"[ani_convert] file not found: {in_path}")
        return None

    data = bytearray(in_path_obj.read_bytes())

    # what a hell -_- (dec by - brfiles)
    x, y = (0x20, 0x04)
    data[y:y] = data[x:x+4]
    del data[x+4:x+8]

    new_ext = ".ifp"
    new_name = in_path_obj.stem + new_ext
    out_path = Path(out_dir) / new_name
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)

    log.info(f"[ani_convert] saved: {out_path}")
    return str(in_path), str(out_path)

async def semaphore(ani_path, out_dir):
    async with SEMAPHORE:
        return await convert(ani_path, out_dir)

async def batch(input_dir: str, out_dir: str):
    ani_files = list(Path(input_dir).glob("*.ani"))
    if not ani_files:
        log.warning(f"[ani_convert] no ANI files found in {input_dir}")
        return
    tasks = [semaphore(str(p), out_dir) for p in ani_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
