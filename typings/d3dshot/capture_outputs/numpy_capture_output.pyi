"""  # noqa: Y021
This type stub file was generated by pyright.
"""

from numpy import uint8
from numpy.typing import NDArray
from PIL import Image
from d3dshot.capture_output import CaptureOutput


class NumpyCaptureOutput(CaptureOutput):
    def __init__(self) -> None:
        ...

    def process(self, pointer, pitch, size, width, height, region,
                rotation) -> NDArray | NDArray[uint8]:
        ...

    def to_pil(self, frame) -> Image:
        ...

    def stack(self, frames, stack_dimension) -> NDArray:
        ...
