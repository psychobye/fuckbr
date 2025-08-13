import argparse
import asyncio
import logging

from pathlib import Path
from typing import Optional, Tuple

from config import SEMAPHORE

parser = argparse.ArgumentParser(description="DELT")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the DELT")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def convert(in_path: str, out_dir: str) -> Optional[Tuple[str, str]]:
    # TODO: delt decrypt
    log.info(f"[delt_convert] nothing here :3")
    return None

async def semaphore(delt_path, out_dir):
    async with SEMAPHORE:
        return await convert(delt_path, out_dir)

async def batch(input_dir: str, out_dir: str):
    delt_files = list(Path(input_dir).glob("*.delt"))
    if not delt_files:
        log.warning(f"[delt_convert] no DELT files found in {input_dir}")
        return
    tasks = [semaphore(str(p), out_dir) for p in delt_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
