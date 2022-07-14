from __future__ import annotations

from typing import TYPE_CHECKING

import cv2
import numpy as np
import pyautogui
from PIL import Image

from capture_method.interface import CaptureMethodInterface

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class PyAutoGUICaptureMethod(CaptureMethodInterface):
    _render_full_content = False

    def get_frame(self, autosplit: AutoSplit):
        selection = autosplit.settings_dict["capture_region"]
        img: Image.Image = pyautogui.screenshot()
        frame = np.array(img)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame, False

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return True
