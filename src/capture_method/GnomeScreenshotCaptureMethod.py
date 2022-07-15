from capture_method.XDisplayCaptureMethod import XDisplayCaptureMethod


class GnomeScreenshotCaptureMethod(XDisplayCaptureMethod):   # pylint: disable=abstract-method
    _xdisplay = None
