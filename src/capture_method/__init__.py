from __future__ import annotations

import asyncio
import os
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, TypedDict

import cv2

from capture_method.interface import CaptureMethodInterface
from capture_method.PyAutoGUICaptureMethod import PyAutoGUICaptureMethod
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from utils import IS_LINUX, IS_WINDOWS, WINDOWS_BUILD_NUMBER

if IS_WINDOWS:
    from pygrabber.dshow_graph import FilterGraph
    from winsdk.windows.media.capture import MediaCapture

    from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
    from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
    from capture_method.ForceFullContentRenderingCaptureMethod import ForceFullContentRenderingCaptureMethod
    from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_MIN_BUILD = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


@dataclass
class CaptureMethodInfo():
    name: str
    short_description: str
    description: str
    implementation: type[CaptureMethodInterface]


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(self, other: str):
        try:
            self(other)  # pyright: ignore [reportGeneralTypeIssues]
        except ValueError:
            return False
        else:
            return True


@unique
class CaptureMethodEnum(Enum, metaclass=CaptureMethodMeta):
    # Allow TOML to save as a simple string
    def __repr__(self):
        return self.value
    __str__ = __repr__

    # Allow direct comparison with strings
    def __eq__(self, other: object):
        return self.value == other.__str__()

    # Restore hashing functionality
    def __hash__(self):
        return self.value.__hash__()

    BITBLT = "BITBLT"
    WINDOWS_GRAPHICS_CAPTURE = "WINDOWS_GRAPHICS_CAPTURE"
    PRINTWINDOW_RENDERFULLCONTENT = "PRINTWINDOW_RENDERFULLCONTENT"
    DESKTOP_DUPLICATION = "DESKTOP_DUPLICATION"
    PY_AUTO_GUI = "PY_AUTO_GUI"
    VIDEO_CAPTURE_DEVICE = "VIDEO_CAPTURE_DEVICE"


class CaptureMethodDict(OrderedDict[CaptureMethodEnum, CaptureMethodInfo]):
    def get_method_by_index(self, index: int):
        if index < 0:
            return next(iter(self))
        return list(self.keys())[index]


CAPTURE_METHODS = CaptureMethodDict()
if IS_WINDOWS:
    def test_for_media_capture():
        async def coroutine():
            return await (MediaCapture().initialize_async() or asyncio.sleep(0))
        try:
            asyncio.run(coroutine())
            return True
        except OSError:
            return False

    CAPTURE_METHODS[CaptureMethodEnum.BITBLT] = CaptureMethodInfo(
        name="BitBlt",
        short_description="fastest, least compatible",
        description=(
            "\nA good default fast option. But it cannot properly record "
            "\nOpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
            "\nThe smaller the selected region, the more efficient it is. "
        ),

        implementation=BitBltCaptureMethod,
    )
    if (  # Windows Graphics Capture requires a minimum Windows Build
        WINDOWS_BUILD_NUMBER < WGC_MIN_BUILD
        # Our current implementation of Windows Graphics Capture requires at least one CaptureDevice
        or not test_for_media_capture()
    ):
        CAPTURE_METHODS[CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE] = CaptureMethodInfo(
            name="Windows Graphics Capture",
            short_description="fast, most compatible, capped at 60fps",
            description=(
                f"\nOnly available in Windows 10.0.{WGC_MIN_BUILD} and up. "
                "\nDue to current technical limitations, it requires having at least one "
                "\naudio or video Capture Device connected and enabled. Even if it won't be used. "
                "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
                "\nAdds a yellow border on Windows 10 (not on Windows 11)."
                "\nCaps at around 60 FPS. "
            ),
            implementation=WindowsGraphicsCaptureMethod,
        )
    CAPTURE_METHODS[CaptureMethodEnum.DESKTOP_DUPLICATION] = CaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="slower, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
             "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
            "\nOverlapping windows will show up and can't record across displays. "
        ),
        implementation=DesktopDuplicationCaptureMethod,
    )
    CAPTURE_METHODS[CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT] = CaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
             "\nto PrintWindow to force rendering the entire desktop. "
            "\nAbout 10-15x slower than BitBlt based on original window size "
            "\nand can mess up some applications' rendering pipelines. "
        ),
        implementation=ForceFullContentRenderingCaptureMethod,
    )
elif IS_LINUX:
    CAPTURE_METHODS[CaptureMethodEnum.PY_AUTO_GUI] = CaptureMethodInfo(
        name="PyAutoGUI",
        short_description="screenshots using PyAutoGUI",
        description=(
            "\nUses PyAutoGUI to take screenshots "
            "\n\"scrot\" must be installed to use screenshot functions in Linux. Run: sudo apt-get install scrot"
        ),
        implementation=PyAutoGUICaptureMethod,
    )

CAPTURE_METHODS[CaptureMethodEnum.VIDEO_CAPTURE_DEVICE] = CaptureMethodInfo(
    name="Video Capture Device",
    short_description="very slow, see below",
    description=(
        "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
        "\nYou can select one below. "
        "\nThere are currently performance issues, but it might be more convenient. "
        "\nIf you want to use this with OBS' Virtual Camera, use the Virtualcam plugin instead "
        "\nhttps://obsproject.com/forum/resources/obs-virtualcam.949/."
    ),
    implementation=VideoCaptureDeviceCaptureMethod,
)


def change_capture_method(selected_capture_method: CaptureMethodEnum, autosplit: AutoSplit):
    autosplit.capture_method.close(autosplit)
    autosplit.capture_method = CAPTURE_METHODS[selected_capture_method].implementation(autosplit)
    if selected_capture_method == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
        autosplit.select_region_button.setDisabled(True)
        autosplit.select_window_button.setDisabled(True)
    else:
        autosplit.select_region_button.setDisabled(False)
        autosplit.select_window_button.setDisabled(False)


@dataclass
class CameraInfo():
    device_id: int
    name: str
    occupied: bool
    backend: str


def get_input_devices() -> list[str]:
    if IS_WINDOWS:
        return FilterGraph().get_input_devices()
    if IS_LINUX:
        cameras: list[str] = []
        for index in range(len(os.listdir("/sys/class/video4linux"))):
            with open(f"/sys/class/video4linux/video{index}/name", "r", encoding="utf-8") as file:
                cameras.append(file.readline()[:-2])
        return cameras
    return []


async def get_all_video_capture_devices():
    named_video_inputs = get_input_devices()

    async def get_camera_info(index: int, device_name: str):
        video_capture = cv2.VideoCapture(index)
        video_capture.setExceptionMode(True)
        backend = ""
        try:
            # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
            backend = video_capture.getBackendName()
            video_capture.grab()
        except cv2.error as error:  # pyright: ignore [reportUnknownVariableType]
            return CameraInfo(index, device_name, True, backend) \
                if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT) \
                else None
        finally:
            video_capture.release()
        return CameraInfo(index, device_name, False, backend)

    future = asyncio.gather(*[
        get_camera_info(index, name) for index, name
        in enumerate(named_video_inputs)
    ])

    return [
        camera_info for camera_info
        in await future
        if camera_info is not None]
