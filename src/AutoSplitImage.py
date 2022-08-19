from __future__ import annotations

import os
from enum import Enum
from math import sqrt
from typing import TYPE_CHECKING, Optional, Union

import cv2
import numpy as np
from win32con import MAXBYTE

import error_messages
from compare import check_if_image_has_transparency, compare_histograms, compare_l2_norm, compare_phash
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# Resize to these width and height so that FPS performance increases
COMPARISON_RESIZE_RESOLUTION = 320 * 240
START_KEYWORD = "start_auto_splitter"
RESET_KEYWORD = "reset"


class ImageType(Enum):
    SPLIT = 0
    RESET = 1
    START = 2


class AutoSplitImage():
    path: str
    filename: str
    flags: int
    loops: int
    image_type: ImageType
    bytes: Optional[cv2.Mat] = None
    mask: Optional[cv2.Mat] = None
    # This value is internal, check for mask instead
    _has_transparency = False
    # These values should be overriden by Defaults if None. Use getters instead
    __delay_time: Optional[float] = None
    __comparison_method: Optional[int] = None
    __pause_time: Optional[float] = None
    __similarity_threshold: Optional[float] = None

    def get_delay_time(self, default: Union[AutoSplit, int]):
        """
        Get image's delay time or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, int) \
            else default.settings_dict["default_delay_time"]
        return default_value if self.__delay_time is None else self.__delay_time

    def __get_comparison_method(self, default: Union[AutoSplit, int]):
        """
        Get image's comparison or fallback to the default value from combobox
        """
        default_value = default \
            if isinstance(default, int) \
            else default.settings_dict["default_comparison_method"]
        return default_value if self.__comparison_method is None else self.__comparison_method

    def get_pause_time(self, default: Union[AutoSplit, float]):
        """
        Get image's pause time or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, float) \
            else default.settings_dict["default_pause_time"]
        return default_value if self.__pause_time is None else self.__pause_time

    def get_similarity_threshold(self, default: Union[AutoSplit, float]):
        """
        Get image's similarity threshold or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, float) \
            else default.settings_dict["default_similarity_threshold"]
        return default_value if self.__similarity_threshold is None else self.__similarity_threshold

    def __init__(self, path: str):
        self.path = path
        self.filename = os.path.split(path)[-1].lower()
        self.flags = flags_from_filename(self.filename)
        self.loops = loop_from_filename(self.filename)
        self.__delay_time = delay_time_from_filename(self.filename)
        self.__comparison_method = comparison_method_from_filename(self.filename)
        self.__pause_time = pause_from_filename(self.filename)
        self.__similarity_threshold = threshold_from_filename(self.filename)
        self.__read_image_bytes(path)

        if START_KEYWORD in self.filename:
            self.image_type = ImageType.START
        elif RESET_KEYWORD in self.filename:
            self.image_type = ImageType.RESET
        else:
            self.image_type = ImageType.SPLIT

    def __read_image_bytes(self, path: str):
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if not is_valid_image(image):
            self.bytes = None
            error_messages.image_type(path)
            return

        self._has_transparency = check_if_image_has_transparency(image)
        if self._has_transparency:
            image_bgr, image_alpha = image[:, :, :3], image[:, :, 3]
            scale = sqrt(min(1, COMPARISON_RESIZE_RESOLUTION / cv2.countNonZero(image_alpha)))
            image_bgr = cv2.resize(image_bgr, dsize=None, fx=scale, fy=scale)
            image_alpha = cv2.resize(image_alpha, dsize=None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
            image = np.dstack((image_bgr, image_alpha))
            # If image has transparency, create a mask
            # Create mask based on resized, nearest neighbor interpolated split image
            self.mask = cv2.inRange(image_alpha, np.array([1], dtype="uint8"), np.array([MAXBYTE], dtype="uint8"))
        else:
            image_height, image_width = image.shape[:2]
            image_resolution = image_height * image_width
            scale = sqrt(COMPARISON_RESIZE_RESOLUTION / image_resolution)
            image = cv2.resize(image, dsize=None, fx=scale, fy=scale)
            # Add Alpha channel if missing
            if image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        self.bytes = image

    def check_flag(self, flag: int):
        return self.flags & flag == flag

    def compare_with_capture(
        self,
        default: Union[AutoSplit, int],
        capture: Optional[cv2.Mat]
    ):
        """
        Compare image with capture using image's comparison method. Falls back to combobox
        """

        if not is_valid_image(self.bytes) or not is_valid_image(capture):
            return 0.0
        capture = cv2.resize(capture, self.bytes.shape[1::-1])
        comparison_method = self.__get_comparison_method(default)
        if comparison_method == 0:
            return compare_l2_norm(self.bytes, capture, self.mask)
        if comparison_method == 1:
            return compare_histograms(self.bytes, capture, self.mask)
        if comparison_method == 2:
            return compare_phash(self.bytes, capture, self.mask)
        return 0.0


if True:  # pylint: disable=using-constant-test
    from split_parser import (comparison_method_from_filename, delay_time_from_filename, flags_from_filename,
                              loop_from_filename, pause_from_filename, threshold_from_filename)
