"""  # noqa: Y021
This type stub file was generated by pyright.
"""

import ctypes
from typing import Any

#


class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = ...


def get_display_device_name_mapping() -> dict:
    ...


def get_hmonitor_by_point(x, y) -> Any:
    ...