# decryption tools for .bpc, .mod, and .btx files

this repository contains three python scripts:

- `bpc.py` — decrypts `.bpc` files into `.zip`
- `mod.py` — decrypts `.mod` files into `.dff`
- `btx.py` — decrypts `.btx` files into `.png`

## requirements

- python 3.9 (required for `PVRTexLibPy`)
- all dependencies listed in `requirements.txt`

---

## how to use `bpc.py`

decrypts a single `.bpc` file into a `.zip` archive using a static xor key.

### usage

```
python bpc.py path/to/file.bpc
```

- output: `file.zip` in the same directory  
- only one file at a time  
- no folder structure needed  

example output: `data/test_asset.zip`

---

## how to use `mod.py`

decrypts all `.mod` files in the `mod/` folder using a custom TEA-based algorithm and saves them as `.dff`.

- input folder: `mod/`
- output folder: `dff/` (created automatically)

### usage

```
python mod.py
```

- scans the `mod/` folder  
- outputs `.dff` files to `dff/`

---

## how to use `btx.py`

decrypts all `.btx` files in the `btx/` folder using `PVRTexLibPy` and saves them as `.png`.

- input folder: `btx/`
- output folder: `png/` (created automatically)

### usage

```
python btx.py
```

- scans the `btx/` folder  
- outputs `.png` files to `png/`