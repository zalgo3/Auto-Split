import sys

# https://stackoverflow.com/a/65051692
if sys.platform == "linux":
    hiddenimports = ["pynput.keyboard._xorg", "pynput.mouse._xorg"]
