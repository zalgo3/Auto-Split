import os
import sys

# https://stackoverflow.com/a/65051692
# https://github.com/moses-palmer/pynput/blob/master/lib/pynput/_util/__init__.py#L55
backend_name = os.environ.get(
    "PYNPUT_BACKEND_KEYBOARD",
    os.environ.get("PYNPUT_BACKEND", None))
if backend_name:
    module = backend_name
elif sys.platform == "darwin":
    module = "darwin"
elif sys.platform == "win32":
    module = "win32"
else:
    module = "xorg"

hiddenimports = ["pynput.keyboard._{module}"]
