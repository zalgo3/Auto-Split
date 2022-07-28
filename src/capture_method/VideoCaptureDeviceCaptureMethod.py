from __future__ import annotations

from typing import TYPE_CHECKING

import cv2

import error_messages
from capture_method.interface import ThreadedCaptureMethod
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class VideoCaptureDeviceCaptureMethod(ThreadedCaptureMethod):
    capture_device: cv2.VideoCapture

    def _read_action(self, autosplit: AutoSplit):
        result = False
        image = None
        try:
            result, image = self.capture_device.read()
        except cv2.error as error:
            # STS_ERROR most likely means the camera is occupied
            if error.code != cv2.Error.STS_ERROR:
                raise
        except Exception as exception:  # pylint: disable=broad-except # We really want to catch everything here
            error = exception
            self.capture_device.release()
            autosplit.show_error_signal.emit(lambda: error_messages.exception_traceback(
                error,
                "AutoSplit encountered an unhandled exception while trying to grab a frame and has stopped capture. "
                + error_messages.CREATE_NEW_ISSUE_MESSAGE))
        return image if result else None

    def __init__(self, autosplit: AutoSplit):
        self.capture_device = cv2.VideoCapture(autosplit.settings_dict["capture_device_id"])
        self.capture_device.setExceptionMode(True)
        super().__init__(autosplit)

    def close(self, autosplit: AutoSplit, from_exception: bool = False):
        super().close(autosplit, from_exception)
        self.capture_device.release()

    def get_frame(self, autosplit: AutoSplit):
        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image

        selection = autosplit.settings_dict["capture_region"]
        # Ensure we can't go OOB of the image
        y = min(selection["y"], image.shape[0] - 1)
        x = min(selection["x"], image.shape[1] - 1)
        image = image[
            y:y + selection["height"],
            x:x + selection["width"],
        ]
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA), is_old_image

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return bool(self.capture_device.isOpened())
