from win32 import win32gui
import mss
import numpy
import win32ui
import win32con


def capture_region(hwnd, rect, legacy_capture):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param rect: The coordinates of the region
    @param legacy_capture: Use the python-mss library - potentially less performance
    @return: The image of the region in the window in BGRA format
    """

    if legacy_capture:
        return _capture_region_win32(hwnd, rect)

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    # Get the top left of the window coordinates
    coordinates = win32gui.GetWindowRect(hwnd)
    window_coord_x = coordinates[0]
    window_coord_y = coordinates[1]

    # TEST - does this work for DPI scaled windows?
    # TEST - does this work for multi-monitor setups?
    with mss.mss() as sct:
        region = {
            "top": window_coord_y + rect.top,
            "left": window_coord_x + rect.left,
            "width": width,
            "height": height,
        }
        img = numpy.array(sct.grab(region))

    # TODO - there seems to be big performance gains to be made by optimizing the color conversions
    # - this would be relevant python-mss or not.
    # - https://github.com/BoboTiG/python-mss/blob/5c0c4f6215c33d0a60ca9c67f2ef1bc8fa632380/mss/tests/bench_bgra2rgb.py
    return img


def _capture_region_win32(hwnd, rect):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param rect: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dcObj, width, height)
    cDC.SelectObject(bmp)
    cDC.BitBlt((0, 0), (width, height), dcObj, (rect.left, rect.top), win32con.SRCCOPY)

    img = bmp.GetBitmapBits(True)
    img = numpy.frombuffer(img, dtype='uint8')
    img.shape = (height, width, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(bmp.GetHandle())

    return img
