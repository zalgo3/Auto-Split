import sys

if sys.platform != "win32":
    raise OSError()

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod


class ForceFullContentRenderingCaptureMethod(BitBltCaptureMethod):  # pylint: disable=too-few-public-methods
    _render_full_content = True
