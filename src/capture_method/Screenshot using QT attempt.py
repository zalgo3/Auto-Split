from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageGrab
from PyQt6.QtCore import QBuffer, QCoreApplication, QIODevice, QIODeviceBase
from PyQt6.QtGui import QGuiApplication, QPixmap, QScreen
from PyQt6.QtWidgets import QApplication, QWidget

from capture_method.interface import CaptureMethodInterface

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class ScrotCaptureMethod(CaptureMethodInterface):
    _render_full_content = False

    def get_frame(self, autosplit: AutoSplit):
        buffer = QBuffer()
        buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        winid = autosplit.winId()
        test = QGuiApplication.primaryScreen().grabWindow(winid, 0, 0, 200, 200)
        image = test.toImage()
        b = image.bits()
        # sip.voidptr must know size to support python buffer interface
        b.setsize(200 * 200 * 3)
        frame = np.frombuffer(b, np.uint8).reshape((200, 200, 3))

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame, False

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return True
