from PyInstaller.building.build_main import Analysis  # type: ignore[import]

class PostGraphAPI:
    @property
    def __path__(self) -> tuple[str, ...] | None: ...
    @property
    def analysis(self) -> Analysis: ...
