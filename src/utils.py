import asyncio
import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
from collections.abc import Callable, Iterable
from platform import version
from sys import platform
from typing import Any, Optional, TypeVar, Union, cast

import cv2
from typing_extensions import TypeGuard

IS_WINDOWS = platform.startswith("win")
IS_LINUX = platform.startswith("linux")
if IS_WINDOWS:
    from win32 import win32gui

DWMWA_EXTENDED_FRAME_BOUNDS = 9


def decimal(value: Union[int, float]):
    return f"{int(value * 100) / 100:.2f}"


def is_digit(value: Optional[Union[str, int]]):
    """
    Checks if `value` is a single-digit string from 0-9
    """
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9
    except (ValueError, TypeError):
        return False


def is_valid_image(image: Optional[cv2.Mat]) -> TypeGuard[cv2.Mat]:
    return image is not None and bool(image.size)


T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key"""
    return next(iter(iterable))


def get_window_bounds(hwnd: int):
    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds))

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = cast(int, extended_frame_bounds.left) - window_rect[0]
    window_top_bounds = cast(int, extended_frame_bounds.top) - window_rect[1]
    window_width = cast(int, extended_frame_bounds.right) - cast(int, extended_frame_bounds.left)
    window_height = cast(int, extended_frame_bounds.bottom) - cast(int, extended_frame_bounds.top)
    return window_left_bounds, window_top_bounds, window_width, window_height


def open_file(file_path: str):
    if IS_WINDOWS:
        os.startfile(file_path)  # nosec
    else:
        opener = "xdg-open" if IS_LINUX else "open"
        subprocess.call([opener, file_path])


def fire_and_forget(func: Callable[..., None]):
    def wrapped(*args: Any, **kwargs: Any):
        return asyncio.get_event_loop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[2]) if platform == "win32" else -1
FIRST_WIN_11_BUILD = 22000
"""AutoSplit Version number"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either the AutoSplit executable or AutoSplit.py"""

# Shared values
AUTOSPLIT_VERSION = "2.0.0-alpha.4"
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
MAXBYTE = 255
