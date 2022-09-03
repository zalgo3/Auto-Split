from collections.abc import Callable, Generator, Sequence
from ctypes import CDLL
from typing import TypeVar

from _typeshed import Incomplete
from keyboard._canonical_names import normalize_name as normalize_name
from keyboard._keyboard_event import KEY_DOWN as KEY_DOWN, KEY_UP as KEY_UP, KeyboardEvent as KeyboardEvent
from typing_extensions import TypeAlias

_Unused: TypeAlias = object

# https://github.com/ronaldoussoren/pyobjc/milestone/3
_CGEventTap: TypeAlias = Incomplete  # Quartz.CGEventTap
_KCGEvent: TypeAlias = Incomplete  # Quartz.kCGEvent
_T = TypeVar("_T")

unichr = chr
Carbon: CDLL


class KeyMap:
    non_layout_keys: dict[int, str]
    layout_specific_keys: dict[int, tuple[str, str]]
    def character_to_vk(self, character: str) -> tuple[int, list[str]]: ...
    def vk_to_character(self, vk: int, modifiers: Sequence[str] = ...): ...


class KeyController:
    key_map: KeyMap
    current_modifiers: dict[str, bool]
    media_keys: dict[str, int]
    def press(self, key_code: int) -> None: ...
    def release(self, key_code: int) -> None: ...
    def map_char(self, character: str) -> tuple[int, list[str]]: ...
    def map_scan_code(self, scan_code: int) -> int | str | None: ...


class KeyEventListener:
    blocking: bool
    callback: Callable[[KeyboardEvent], None]
    listening: bool
    tap: _CGEventTap
    def __init__(self, callback: Callable[[KeyboardEvent], None], blocking: bool = ...) -> None: ...
    def run(self) -> None: ...
    def handler(self, proxy: _Unused, e_type: _KCGEvent, event: _T, refcon: _Unused) -> _T: ...


key_controller: KeyController


def init() -> None: ...
def press(scan_code: int) -> None: ...
def release(scan_code: int) -> None: ...
def map_name(name: str) -> Generator[tuple[int, list[str]], None, None]: ...
def name_from_scancode(scan_code: int) -> int | str | None: ...
def listen(callback: Callable[[KeyboardEvent], None]) -> None: ...
def type_unicode(character: str) -> None: ...
