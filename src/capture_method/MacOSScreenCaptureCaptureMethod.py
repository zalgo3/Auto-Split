from __future__ import annotations

import sys

if sys.platform != "linux" and sys.platform != "darwin":
    raise OSError()

from typing import TYPE_CHECKING

import cv2
import numpy as np
from PIL import ImageGrab
from pywinctl import getWindowsWithTitle

from capture_method.interface import ThreadedCaptureMethod
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class MacOSScreenCaptureCaptureMethod(ThreadedCaptureMethod):
    def _read_action(self, autosplit: AutoSplit):
        if not self.check_selected_region_exists(autosplit):
            return None
        offset_x = 0
        offset_y = 0

        selection = autosplit.settings_dict["capture_region"]
        x = selection["x"] + offset_x
        y = selection["y"] + offset_y
        image = ImageGrab.grab(
            (x,
             y,
             x + selection["width"],
             y + selection["height"]))
        return np.array(image)

    def get_frame(self, autosplit: AutoSplit):
        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA), is_old_image

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit):
        windows = getWindowsWithTitle(captured_window_title)
        if len(windows) <= 0:
            return False
        autosplit.hwnd = windows[0].getHandle()
        return self.check_selected_region_exists(autosplit)
