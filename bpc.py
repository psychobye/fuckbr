import argparse
import logging

from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="BPC")
parser.add_argument("-i", "--input", type=str, required=True, help="path to the BPC")
args = parser.parse_args()

key = b"1cK1a5UF2tU8*G2lW#&%"

def decrypt(bpc_bytes: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(bpc_bytes))

def convert(filepath: str) -> str:
    if not Path(filepath).is_file():
        log.warning(f"[bpc_convert] file not found: {filepath}")
        return None

    logging.info(f"[bpc_convert] starting conversion for {filepath}")
    with open(filepath, 'rb') as f:
        data = f.read()
    dec = decrypt(data)
    base = Path(filepath).stem + ".zip"
    out_path = Path(filepath).parent / base
    with open(out_path, 'wb') as f:
        f.write(dec)

    logging.info(f"[bpc_convert] file saved in {out_path}")
    return out_path

def main():
    convert(args.input)

if __name__ == "__main__":
    main()
