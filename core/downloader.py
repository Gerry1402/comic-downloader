from time import sleep
from zipfile import ZIP_STORED, ZipFile

from core.comic import Comic
from core.file_manager import FileManager
from core.image import Image
from core.logger import Logger
from core.scraper import Scraper
from utils.utils import threadpool


class Downloader:
    retries: int = 3
    time_between_retries: int = 8

    def __init__(self, comic: Comic, scraper: Scraper) -> None:
        self.comic: Comic = comic
        self.scraper: Scraper = scraper(comic)
        self.file_manager: FileManager = FileManager(comic)
        self.logger: Logger = Logger("download", comic)

    def get_missing_episodes(self) -> set[int]:
        self._print(status="Searching missing episodes...")
        avalaible = self.scraper.get_avalaible_episodes()
        downloaded = self.file_manager.get_downloaded_episodes()
        self.logger.add("missing_episodes", len(avalaible) < len(downloaded), comic_url=self.scraper.url_comic())
        return avalaible - downloaded - {0}

    def attempt_download_episode(self, episode: int, urls: list[str], workers: int) -> bool:
        images: list[bytes | None, bytes | None] = [None, None]
        path, extension = self.file_manager.path(episode), self.file_manager.extension
        with ZipFile(path.with_suffix(extension), "w", compression=ZIP_STORED) as cbz_f:

            def write_image_indexed(i: int, content: bytes, ext: str) -> None:
                with cbz_f.open(f"{i:03}{ext}", "w") as f:
                    f.write(content)

            for i, result in threadpool(self.scraper._get_image_content, urls, workers=workers):
                if result is None:
                    return True
                content, ext = result
                if not all(images):
                    images[int(i != 1)] = content
                    if all(images) and Image.equal_widths(*images):
                        write_image_indexed(i, images[0], ext)
                if i != 1:
                    write_image_indexed(i, content, ext)

        return False

    def download_episode(self, episode: int | float, workers: int = 15) -> bool:
        self._print(status=f"Searching episode {episode}...")
        urls = self.scraper.get_url_images_episode(episode)
        self._print(status=f"Downloading episode {episode}...")
        for i in range(self.retries):
            if has_errors := self.attempt_download_episode(episode, urls, workers):
                self.file_manager.path(episode).unlink(missing_ok=True)
            elif i == self.retries - 1 or not has_errors:
                break
            self._print(status=f"Downloading episode {episode} - Attempt {i + 2}...")
            sleep(self.time_between_retries)
        self.logger.add("download_episode", has_errors, episode=episode, urls=len(urls), referer=self.scraper.REFERER)

    def download_all(self, workers: int = 15) -> None:
        for episode in self.get_missing_episodes():
            self.download_episode(episode, workers)
        self._print(status="Downloaded", end="\n")

    def _print(self, end: str = "", **kwargs: str | int) -> None:
        content = ", ".join(f"{key}: {value}" for key, value in kwargs.items())
        print(f"\r\033[K{self.comic.title} -> (source: {self.comic.source},  {content})", end=end)
