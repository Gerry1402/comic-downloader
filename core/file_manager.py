from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from config import get_settings
from core.comic import Comic


class FileManager:
    base_path: Path = get_settings().base_path
    extension = ".cbz"
    z_fill: int = 4

    def __init__(self, comic: Comic) -> None:
        self.comic = comic
        self._cbz: ZipFile | None = None

    def path(self, episode: int | str | None = None) -> Path:
        path = self.base_path / self.comic.name
        path.mkdir(parents=True, exist_ok=True)
        if episode is None:
            return path
        return path / f"{str(episode).zfill(self.z_fill)}{self.extension}"

    def get_downloaded_episodes(self) -> set[int]:
        return {int(file.stem) for file in self.path().rglob(f"*{self.extension}")}

    def delete(self, episode: int) -> None:
        self.path(episode).with_suffix(self.extension).unlink(missing_ok=True)

    def open(self, episode: int) -> None:
        self._cbz = ZipFile(self.path(episode).with_suffix(self.extension), "w", compression=ZIP_STORED)

    def write(self, i: int, content: bytes, ext: str) -> None:
        with self._cbz.open(f"{i:03}{ext}", "w") as f:
            f.write(content)

    def close(self) -> None:
        if self._cbz:
            self._cbz.close()
            self._cbz = None
