from __future__ import annotations

from threading import Event, Thread
from typing import TYPE_CHECKING, Optional

import cv2

from error_messages import CREATE_NEW_ISSUE_MESSAGE, exception_traceback

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodInterface():
    def __init__(self, autosplit: Optional[AutoSplit] = None):
        pass

    def reinitialize(self, autosplit: AutoSplit):
        self.close(autosplit)
        self.__init__(autosplit)  # pylint: disable=unnecessary-dunder-call

    def close(self, autosplit: AutoSplit):
        pass

    def get_frame(self, autosplit: AutoSplit) -> tuple[Optional[cv2.Mat], bool]:
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box

        @return: The image of the region in the window in BGRA format
        """
        raise NotImplementedError()

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()

    def check_selected_region_exists(self, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()


class ThreadedCaptureMethod(CaptureMethodInterface):
    __capture_thread: Optional[Thread]
    __last_captured_frame: Optional[cv2.Mat] = None
    __is_old_image = False
    __stop_thread = Event()

    def _read_action(self, autosplit: AutoSplit) -> Optional[cv2.Mat]:
        raise NotImplementedError()

    def __read_loop(self, autosplit: AutoSplit):
        try:
            while not self.__stop_thread.is_set():
                self.__last_captured_frame = self._read_action(autosplit)
                self.__is_old_image = False
        except Exception as exception:  # pylint: disable=broad-except # We really want to catch everything here
            error = exception
            autosplit.show_error_signal.emit(lambda: exception_traceback(
                "AutoSplit encountered an unhandled exception while trying to grab a frame and has stopped capture. "
                + CREATE_NEW_ISSUE_MESSAGE,
                error))
            self.close(autosplit, from_exception=True)

    def __init__(self, autosplit: AutoSplit):
        super().__init__()
        self.__stop_thread = Event()
        self.__capture_thread = Thread(target=lambda: self.__read_loop(autosplit))
        self.__capture_thread.start()

    def close(self, autosplit: AutoSplit, from_exception: bool = False):
        self.__stop_thread.set()
        if self.__capture_thread and not from_exception:
            self.__capture_thread.join()
            self.__capture_thread = None

    def get_frame(self, autosplit: AutoSplit) -> tuple[Optional[cv2.Mat], bool]:
        if not self.check_selected_region_exists(autosplit):
            return None, False

        image = self.__last_captured_frame
        is_old_image = self.__is_old_image
        self.__is_old_image = True
        return image, is_old_image
