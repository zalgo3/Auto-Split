from __future__ import annotations

from math import sqrt
from typing import TYPE_CHECKING, Optional

import cv2
import imagehash
import numpy as np
from PIL import Image
from win32con import MAXBYTE

if TYPE_CHECKING:
    from AutoSplitImage import AutoSplitImage

MAXRANGE = MAXBYTE + 1
CHANNELS = [0, 1, 2]
HISTOGRAM_SIZE = [8, 8, 8]
RANGES = [0, MAXRANGE, 0, MAXRANGE, 0, MAXRANGE]
EMPTY = np.empty((0, 0, 0))
MASK_SIZE_MULTIPLIER = 3 * MAXBYTE * MAXBYTE


def compare_l2_norm(source: AutoSplitImage, capture: cv2.ndarray):
    """
    Compares two images by calculating the L2 Error (square-root of sum of squared error)
    @param source: AutoSplitImage
    @param capture: Image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the images as a number 0 to 1.
    """
    source_bytes = EMPTY if source.bytes is None else source.bytes
    # https://github.com/microsoft/pylance-release/issues/2089
    error = cv2.norm(source_bytes, capture, cv2.NORM_L2, source.mask)  # pyright: ignore

    # The L2 Error is summed across all pixels, so this normalizes
    if not source.cached_l2_norm_max_error:
        source.cached_l2_norm_max_error = sqrt(source_bytes.size) * MAXBYTE \
            if source.mask is None or not source.mask.size\
            else sqrt(np.count_nonzero(source.mask) * MASK_SIZE_MULTIPLIER)

    if not source.cached_l2_norm_max_error:
        return 0.0
    return 1 - (error / source.cached_l2_norm_max_error)


def compare_histograms(source: AutoSplitImage, capture: cv2.ndarray):
    """
    Compares two images by calculating their histograms, normalizing
    them, and then comparing them using Bhattacharyya distance.

    @param source: AutoSplitImage
    @param capture: An image matching the dimensions of the source
    @return: The similarity between the histograms as a number 0 to 1.
    """

    if source.cached_histogram is None:
        source_bytes = EMPTY if source.bytes is None else source.bytes
        source_hist = cv2.calcHist([source_bytes], CHANNELS, source.mask, HISTOGRAM_SIZE, RANGES)
        cv2.normalize(source_hist, source_hist)
        source.cached_histogram = source_hist

    capture_hist = cv2.calcHist([capture], CHANNELS, source.mask, HISTOGRAM_SIZE, RANGES)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source.cached_histogram, capture_hist, cv2.HISTCMP_BHATTACHARYYA)


def compare_phash(source: AutoSplitImage, capture: cv2.ndarray):
    """
    Compares the Perceptual Hash of the two given images and returns the similarity between the two.

    @param source: AutoSplitImage
    @param capture: Image of any given shape as a numpy array
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the hashes of the image as a number 0 to 1.
    """
    if not source.cached_phash:
        source_bytes = EMPTY if source.bytes is None else source.bytes
        # Same comment as below
        if source.mask is not None and source.mask.size:
            source_bytes = cv2.bitwise_and(source_bytes, source_bytes, mask=source.mask)
        source.cached_phash = imagehash.phash(Image.fromarray(source_bytes))

    # Since imagehash doesn't have any masking itself, bitwise_and will allow us
    # to apply the mask to the source and capture before calculating the pHash for
    # each of the images. As a result of this, this function is not going to be very
    # helpful for large masks as the images when shrinked down to 8x8 will mostly be
    # the same
    if source.mask is not None and source.mask.size:
        capture = cv2.bitwise_and(capture, capture, mask=source.mask)
    capture_hash = imagehash.phash(Image.fromarray(capture))

    hash_diff = source.cached_phash - capture_hash
    if not hash_diff:
        return 0.0
    return 1 - (hash_diff / 64.0)


def compare_template(source: cv2.ndarray, capture: cv2.ndarray, mask: Optional[cv2.ndarray] = None):
    """
    Checks if the source is located within the capture by using the sum of square differences.
    The mask is used to search for non-rectangular images within the capture

    @param source: The subsection being searched for within the capture
    @param capture: Capture of an image larger than the source
    @param mask: The mask of the source with the same dimensions
    @return: The best similarity for a region found in the image. This is
    represented as a number from 0 to 1.
    """

    result = cv2.matchTemplate(capture, source, cv2.TM_SQDIFF, mask=mask)
    min_val, *_ = cv2.minMaxLoc(result)

    # matchTemplate returns the sum of square differences, this is the max
    # that the value can be. Used for normalizing from 0 to 1.
    max_error = source.size * MAXBYTE * MAXBYTE \
        if mask is None or not mask.size \
        else np.count_nonzero(mask)

    return 1 - (min_val / max_error)


def check_if_image_has_transparency(image: cv2.ndarray):
    # Check if there's a transparency channel (4th channel) and if at least one pixel is transparent (< 255)
    if image.shape[2] != 4:
        return False
    mean: float = np.mean(image[:, :, 3])
    if mean == 0:
        # Non-transparent images code path is usually faster and simpler, so let's return that
        return False
        # TODO error message if all pixels are transparent
        # (the image appears as all black in windows, so it's not obvious for the user what they did wrong)

    return mean != 255
