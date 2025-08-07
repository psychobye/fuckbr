import argparse
import asyncio
import logging

from pathlib import Path
from typing import Optional, Tuple

parser = argparse.ArgumentParser(description="ANI")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the ANI")
parser.add_argument("-o", "--output", type=str, required=True, help="output directory")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def convert(in_path: str, out_dir: str) -> Optional[Tuple[str, str]]:
    if not Path(in_path).is_file():
        log.warning(f"[ani_convert] file not found: {in_path}")
        return None

    # legendary dec by psychobe xD
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    in_path_obj = Path(in_path)
    new_name = in_path_obj.stem + ".ifp"
    out_path = out_dir_path / new_name

    # just rename file ani to ifp LOL
    out_path.write_bytes(in_path_obj.read_bytes())

    log.info(f"[ani_convert] saved: {out_path}")
    return str(in_path), str(out_path)

async def batch(input_dir: str, out_dir: str):
    ani_files = list(Path(input_dir).glob("*.ani"))
    if not ani_files:
        log.warning(f"[ani_convert] no ANI files found in {input_dir}")
        return
    tasks = [asyncio.to_thread(convert, str(p), out_dir) for p in ani_files]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(batch(args.input, args.output))

if __name__ == "__main__":
    main()
