pyinstaller --onefile --windowed ^
--collect-all numpy ^
--icon=icon.ico ^
--add-data "icon.ico;." ^
--add-binary "PVRTexLibPy.pyd;." ^
--add-binary "PVRTexLib.dll;." ^
unware.py