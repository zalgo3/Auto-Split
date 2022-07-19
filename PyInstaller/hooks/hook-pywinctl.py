import sys

if sys.platform == "linux":
    hiddenimports = ["pynput.keyboard._xorg"]
