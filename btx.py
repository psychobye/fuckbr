import os
import asyncio
import PVRTexLibPy as pvrpy

BTX_DIR = "btx"
PNG_DIR = "png"

os.makedirs(PNG_DIR, exist_ok=True)

def write_file(path: str, data: bytes):
    with open(path, 'wb') as f:
        f.write(data)

def read_file(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()

async def convert_btx_file(btx_path: str):
    filename = os.path.basename(btx_path)
    base_name = os.path.splitext(filename)[0]
    ktx_path = os.path.join(PNG_DIR, f"{base_name}.ktx")
    png_path = os.path.join(PNG_DIR, f"{base_name}.png")

    try:
        btx_data = read_file(btx_path)
        ktx_data = btx_data[4:]

        write_file(ktx_path, ktx_data)

        texture = pvrpy.PVRTexture(ktx_path)
        if not texture.Decompress(10):
            print(f"[X] decompression failed: {filename}")
            return

        texture.SetTextureColourSpace(pvrpy.ColourSpace.sRGB)

        if not texture.SaveSurfaceToImageFile(png_path):
            print(f"[X] couldn't save png: {filename}")
            return

        print(f"[✓] {filename} -> {base_name}.png")

    except Exception as e:
        print(f"[!] error in conversion {filename}: {e}")

    finally:
        if os.path.exists(ktx_path):
            os.remove(ktx_path)

async def main():
    tasks = []
    for fname in os.listdir(BTX_DIR):
        if fname.lower().endswith(".btx"):
            full_path = os.path.join(BTX_DIR, fname)
            tasks.append(convert_btx_file(full_path))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
