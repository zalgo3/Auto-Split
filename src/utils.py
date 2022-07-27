from __future__ import annotations

import asyncio
import os
import subprocess  # nosec B404
import sys
from collections.abc import Callable, Iterable
from platform import version
from sys import platform
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, cast

import cv2

from gen.build_number import AUTOSPLIT_BUILD_NUMBER

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    from win32 import win32gui

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeGuard
    P = ParamSpec("P")

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


def is_valid_hwnd(hwnd: int):
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `\"\"`"""
    if not hwnd:
        return False
    if sys.platform == "win32":
        return bool(win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))
    return True


T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key"""
    return next(iter(iterable))


def get_window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    if sys.platform != "win32":
        raise OSError()

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
    if sys.platform == "win32":
        os.startfile(file_path)  # nosec B606
    else:
        opener = "xdg-open" if sys.platform == "linux" else "open"
        subprocess.call([opener, file_path])   # nosec B603


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()


def fire_and_forget(func: Callable[P, Any]) -> Callable[P, asyncio.Future[None]]:
    """
    Runs synchronous function asynchronously without waiting for a response.
    Uses asyncio to avoid a multitude of possible problems with threads.

    Remember to also wrap the function in a try-except to catch any unhandled exceptions!
    """
    def wrapped(*args: P.args, **kwargs: P.kwargs):
        return get_or_create_eventloop().run_in_executor(None, lambda: func(*args, **kwargs))

    return wrapped


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[2]) if platform == "win32" else -1
FIRST_WIN_11_BUILD = 22000
"""AutoSplit Version number"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either the AutoSplit executable or AutoSplit.py"""
IS_WAYLAND = bool(os.environ.get("WAYLAND_DISPLAY", False))

# Shared strings
# DIRTY_VERSION_EXTENSION = ""
DIRTY_VERSION_EXTENSION = "-" + AUTOSPLIT_BUILD_NUMBER
"""Set DIRTY_VERSION_EXTENSION to an empty string to generate a clean version number"""
AUTOSPLIT_VERSION = "2.0.0-alpha.4" + DIRTY_VERSION_EXTENSION
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
MAXBYTE = 255
