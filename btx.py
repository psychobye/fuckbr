import os
import asyncio
import numpy.core._multiarray_umath
import numpy
import PVRTexLibPy as pvrpy

async def convert_one(btx_path: str, out_dir: str, log=None):
    name = os.path.splitext(os.path.basename(btx_path))[0]
    if log: log(f"[~] BTX → {name}")

    os.makedirs(out_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(btx_path))[0]
    ktx = os.path.join(out_dir, name + ".ktx")
    png = os.path.join(out_dir, name + ".png")
    data = open(btx_path, 'rb').read()
    open(ktx, 'wb').write(data[4:])
    tex = pvrpy.PVRTexture(ktx)
    if not tex.Decompress(10):
        print(f"[X] decompression failed {name}")
        return
    tex.SetTextureColourSpace(pvrpy.ColourSpace.sRGB)
    if not tex.SaveSurfaceToImageFile(png):
        print(f"[X] save png failed {name}")
    else:
        print(f"[✓] {name}.png")
    os.remove(ktx)

async def batch(btx_paths: list, out_dir: str, log=None):
    tasks = [convert_one(p, out_dir, log) for p in btx_paths]
    await asyncio.gather(*tasks)

def convert(btx_paths: list, out_dir: str, log=None):
    asyncio.run(batch(btx_paths, out_dir, log))
