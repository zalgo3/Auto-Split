import sys

if sys.platform != "linux":
    raise OSError()

from capture_method.XDisplayCaptureMethod import XDisplayCaptureMethod


class GnomeScreenshotCaptureMethod(XDisplayCaptureMethod):   # pylint: disable=abstract-method
    _xdisplay = None
