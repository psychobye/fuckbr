pyinstaller --onefile --windowed ^
--collect-all numpy ^
--icon=icon.ico ^
--add-data "icon.ico;." ^
--add-binary "PVRTexLibPy.pyd;." ^
unware.py