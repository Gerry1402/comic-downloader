from pathlib import Path

from config import get_settings
from core.comic import Comic


class FileManager:
    base_path: Path = get_settings().base_path
    extension = ".cbz"
    z_fill: int = 4

    def __init__(self, comic: Comic) -> None:
        self.comic = comic

    def path(self, episode: int | str | None = None) -> Path:
        path = self.base_path / self.comic.name
        path.mkdir(parents=True, exist_ok=True)
        if episode is None:
            return path
        return path / f"{str(episode).zfill(self.z_fill)}{self.extension}"

    def get_downloaded_episodes(self) -> set[int]:
        return {int(file.stem) for file in self.path().rglob(f"*{self.extension}")}
