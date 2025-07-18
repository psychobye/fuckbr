# decryption tools for .bpc and .mod files

this repo contains two python scripts:

- `bpc.py` — decrypts `.bpc` files into `.zip`
- `mod.py` — decrypts `.mod` files into `.dff`

no dependencies required — just python 3.8+.

---

## how to use `bpc.py`

this script takes a single `.bpc` file and decrypts it into a `.zip` file using a static xor key.

### usage:

python bpc.py path/to/file.bpc
the decrypted file will be saved in the same directory as file.zip

only one file at a time

no folders needed

python bpc.py data/test_asset.bpc
# output: data/test_asset.zip

## how to use mod.py
this script decrypts all .mod files in a folder using a TEA-based algorithm and saves the results as .dff files.

default setup:
input folder: mod/

output folder: dff/ (auto-created)

usage:
python mod.py
scans the mod/ directory for .mod files

decrypts and writes .dff files into dff/

example:
mod/
├── car.mod
├── weapon.mod

# run script:
python mod.py

# output:
dff/
├── car.dff
├── weapon.dff
