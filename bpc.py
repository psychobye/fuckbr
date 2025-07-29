import os

key = b"1cK1a5UF2tU8*G2lW#&%"

def decrypt_bpc_to_zip_bytes(bpc_bytes: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(bpc_bytes))

def convert_bpc_file(filepath: str, out_dir: str = None) -> str:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)
    with open(filepath, 'rb') as f:
        data = f.read()
    dec = decrypt_bpc_to_zip_bytes(data)
    base = os.path.splitext(os.path.basename(filepath))[0] + ".zip"
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, base)
    else:
        out_path = os.path.join(os.path.dirname(filepath), base)
    with open(out_path, 'wb') as f:
        f.write(dec)
    return out_path
