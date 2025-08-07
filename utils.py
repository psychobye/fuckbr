import asyncio
import logging

from pathlib import Path
from typing import Optional

from config import (
    KRAM_PATH,
    PVR_PATH
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def write_file(path: Path, data: bytes) -> None:
    await asyncio.to_thread(path.write_bytes, data)

async def read_file(path: Path) -> bytes:
    return await asyncio.to_thread(path.read_bytes)

async def sub_run(*args):
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        log.error(f"[sub_run] command failed with return code {proc.returncode}")
        log.error(f"[sub_run] stderr: {stderr.decode().strip()}")
    return proc.returncode == 0, stderr

async def kram_decode(input_file: str, output_file: str):
    ok, err = await sub_run(KRAM_PATH, "decode", "-i", input_file, "-o", output_file)
    if not ok:
        log.error(f"[kram_decode] kram decode error: {err.decode().strip()}")
    else:
        log.info(f"[kram_decode] kram decode succeeded")
    return ok

async def pvr_decode(input_path: Path, workdir: Path, base: str) -> Optional[Path]: 
    ok, err = await sub_run(
        PVR_PATH,
        "-d", "-f", "r8g8b8a8",
        "-i", str(input_path),
    )
    if not ok:
        log.error(f"[pvr_decode] pvr decode error: {err.decode().strip()}")
        return None

    for p in input_path.parent.iterdir():
        if p.name.startswith(base) and p.suffix == ".png":
            return p

    log.info(f"[pvr_decode] No PNG found for base {base}")
    return None

async def pvr_decode_png(input_path: Path, output_path: Path) -> bool:
    proc = await asyncio.create_subprocess_exec(
        PVR_PATH,
        "-i", str(input_path),
        "-o", str(output_path),
        "-f", "r8g8b8a8",
        "-d",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode:
        log.error(f"[pvr_decode] pvr decode error: {stderr.decode().strip()}")
        return False
    return True
