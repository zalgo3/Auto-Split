from _typeshed import StrOrBytesPath
from collections.abc import Iterable

from PyInstaller.building.datastruct import Target  # type: ignore[import]

class Analysis(Target):
    hooksconfig: dict[str, dict[str, list[str]]]
    def __init__(
        self,
        scripts: Iterable[StrOrBytesPath],
        pathex=...,
        binaries=...,
        datas=...,
        hiddenimports=...,
        hookspath=...,
        hooksconfig: dict[str, dict[str, list[str]]] | None = ...,
        excludes=...,
        runtime_hooks=...,
        cipher=...,
        win_no_prefer_redirects=...,
        win_private_assemblies=...,
        noarchive: bool = ...,
        module_collection_mode=...,
    ) -> None: ...
