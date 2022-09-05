from _typeshed import SupportsKeysAndGetItem
from collections.abc import Iterable

def run(
    pyi_args: Iterable[str] = ...,
    pyi_config: SupportsKeysAndGetItem[str, bool | list[str] | None] | Iterable[tuple[str, bool | list[str] | None]] = ...,
) -> None: ...
