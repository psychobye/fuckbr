import os
import sys

key = b"1cK1a5UF2tU8*G2lW#&%"

def decrypt_bpc_to_zip_bytes(bpc_bytes: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(bpc_bytes))

def convert_bpc_file_to_zip(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        bpc_data = f.read()

    zip_data = decrypt_bpc_to_zip_bytes(bpc_data)

    zip_filename = os.path.splitext(filepath)[0] + ".zip"
    with open(zip_filename, 'wb') as f:
        f.write(zip_data)

    return zip_filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python bpc.py <path_to_file.bpc>")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        print("file not found:", input_path)
        sys.exit(1)

    zip_path = convert_bpc_file_to_zip(input_path)
    print("saved as:", zip_path)
