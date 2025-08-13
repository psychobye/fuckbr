import asyncio
import logging
import argparse

import shutil
import tempfile

from pathlib import Path
from typing import Optional, Tuple

from config import TEMP, SEMAPHORE

from utils import (
    write_file,
    read_file,
    pvr_decode,
    kram_decode
)

parser = argparse.ArgumentParser(description="BTX")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the BTX")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def convert(btx_path: str, out_dir: str) -> Optional[Tuple[bytes, str]]:
    log.info(f"[btx_convert] starting conversion for {btx_path}")

    tmpdir = Path(TEMP) / tempfile.mkdtemp(prefix="btx_")
    outdir = Path(out_dir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)

    base = Path(btx_path).stem
    raw_ktx = tmpdir / f"{base}.ktx"
    dec_ktx = tmpdir / f"{base}_dec.ktx"

    try:
        data = await asyncio.to_thread(lambda: open(btx_path, 'rb').read())
        await write_file(raw_ktx, data[4:])

        if not await kram_decode(raw_ktx, dec_ktx):
            log.error(f"[btx_convert] kram_decode failed for {base}")
            return None

        png_tmp = await pvr_decode(dec_ktx, tmpdir, base)
        if not png_tmp:
            log.error(f"[btx_convert] pvr_decode failed for {base}")
            return None

        final_png = outdir / f"{base}.png"
        await asyncio.to_thread(shutil.move, str(png_tmp), str(final_png))
        png_bytes = await read_file(final_png)

        log.info(f"[btx_convert] conversion successful for {base}")
        return png_bytes, final_png.name

    except Exception as e:
        log.error(f"[btx_convert] error during conversion for {base}: {e}")
        return None

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

async def semaphore(btx_path, out_dir):
    async with SEMAPHORE:
        return await convert(btx_path, out_dir)

async def batch(input_dir: str, out_dir: str):
    btx_files = list(Path(input_dir).glob("*.btx"))
    if not btx_files:
        log.warning(f"[btx_convert] no BTX files found in {input_dir}")
        return
    tasks = [semaphore(str(p), out_dir) for p in btx_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
