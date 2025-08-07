from pathlib import Path
import platform
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BASE_PATH = Path(__file__).parent.resolve()

TEMP = BASE_PATH / "temp"

if platform.system() == "Linux":
    KRAM_PATH = BASE_PATH / "kram/linux/kram"
    PVR_PATH = BASE_PATH / "pvr/linux/PVRTexToolCLI"
elif platform.system() == "Windows":
    KRAM_PATH = BASE_PATH / "kram/win/kram.exe"
    PVR_PATH = BASE_PATH / "pvr/win/PVRTexToolCLI.exe"
else:
    log.error("[X] error: unknown platform")

# MAYBE TO DO FOR MAC? :3