import os
import struct

def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xFFFFFFFF

def tea_decrypt_block(data, key, rounds=8):
    delta = 0x61C88647
    for offset in range(0, len(data), 8):
        v0, v1 = struct.unpack_from('<II', data, offset)
        sum_val = (-delta * rounds) & 0xFFFFFFFF
        for _ in range(rounds):
            v1 = (v1 - ((v0 + sum_val) ^ (key[3] + (v0 >> 5)) ^ (key[2] + (v0 << 4)))) & 0xFFFFFFFF
            new_sum = (sum_val + v1) & 0xFFFFFFFF
            sum_val = (sum_val + delta) & 0xFFFFFFFF
            v0 = (v0 - (new_sum ^ (key[0] + (v1 << 4)) ^ (key[1] + (v1 >> 5)))) & 0xFFFFFFFF
        struct.pack_into('<II', data, offset, v0, v1)

def clean_dff_data(dff_data):
    end = len(dff_data)
    while end > 0 and dff_data[end-1] == 0:
        end -= 1
    return dff_data[:end]

def patch_dff_header(dff_data):
    if len(dff_data) < 12: 
        return dff_data

    real_size = len(dff_data) - 12
    return dff_data[:4] + struct.pack('<I', real_size) + dff_data[8:]

def decrypt_mod_to_dff(mod_bytes):
    magic, length, num_blocks = struct.unpack_from('<III', mod_bytes, 0)
    if magic != 0xAB921033:
        raise ValueError("invalid .mod file")
    base_key = [0x6ED9EE7A, 0x930C666B, 0x930E166B, 0x4709EE79]
    key = [ror32(k ^ 0x12913AFB, 19) for k in base_key]
    data = bytearray(mod_bytes)
    offset = 28
    for i in range(num_blocks):
        block = data[offset : offset + 0x800]
        tea_decrypt_block(block, key, rounds=8)
        data[offset : offset + 0x800] = block
        offset += 0x800
    actual_length = min(length, len(mod_bytes) - 28)
    return bytes(data[28 : 28 + actual_length])

def batch_convert_mods(input_folder='mod', output_folder='dff'):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.mod'):
            mod_path = os.path.join(input_folder, filename)
            with open(mod_path, 'rb') as f:
                try:
                    mod_data = f.read()
                    dff_data = decrypt_mod_to_dff(mod_data)
                    dff_data = patch_dff_header(dff_data)
                    dff_data = clean_dff_data(dff_data)
                    out_path = os.path.join(output_folder, filename.replace('.mod', '.dff'))
                    with open(out_path, 'wb') as out_f:
                        out_f.write(dff_data)
                    print(f'✅ {filename} -> {os.path.basename(out_path)}')
                except Exception as e:
                    print(f'❌ error in {filename}: {e}')

if __name__ == '__main__':
    batch_convert_mods()
