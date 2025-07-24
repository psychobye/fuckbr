# FUCKBR GUI (unware)

this is the graphical interface with decryption tools (`bpc`, `mod`, `btx`, `cls`).

---

## requirements

- **python 3.9 only!** (mandatory for PVRTexLibPy compatibility)  
- all dependencies listed in `requirements.txt`

---

## about the GUI

- all the logic and UI live in `unware.py`  
- this lets you decrypt `.bpc`, `.mod`, `.btx`, and `.cls` files easily with a nice GUI

---

## how to build

just run the provided `build.bat` script in the repo root:

`build.bat`

this will create a single executable `.exe` file in:

`dist/unware.exe`

---

## how to run (dev)

if you want to run the GUI directly from source, just:

`python unware.py`

(make sure you're using python 3.9)

---

## Notes

- the `.exe` includes all needed binaries like `PVRTexLibPy.pyd` 
- the GUI has separate tabs for each format with browse buttons and output folder selectors  
- logs each file processed and shows success/errors in the GUI log box  