""" noqa: Y021
Very incomplete type stub. Fill in as we need
"""


class Size():
    width: float = ...
    height: float = ...


class Frame():
    size: Size = ...


class Screen():
    def frame(self) -> Frame:
        ...


def mainScreen() -> Screen:
    ...
