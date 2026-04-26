from time import sleep

from core.comic import Comic
from core.file_manager import FileManager
from core.image import Image
from core.logger import Logger
from core.scraper import Scraper
from utils.utils import threadpool


class Downloader:
    retries: int = 3
    time_between_retries: int = 8
    workers: int = 15

    def __init__(self, scraper: Scraper) -> None:
        self.comic: Comic = scraper.comic
        self.scraper: Scraper = scraper
        self.file_manager: FileManager = FileManager(self.comic)
        self.log: Logger = Logger("download", self.comic)

    def get_missing_episodes(self) -> set[int]:
        available = self.scraper.get_available_episodes()
        downloaded = self.file_manager.get_downloaded_episodes()
        return available - downloaded - {0}

    def attempt_download_episode(self, episode: int, urls: list[str]) -> bool:
        images: list[bytes | None] = [None, None]
        self.file_manager.open(episode)

        for i, result in threadpool(self.scraper._get_image_content, urls, workers=self.workers):
            if result is None:
                self.file_manager.close()
                return False
            content, ext = result
            if not all(images):
                images[int(i != 1)] = content
                if all(images) and Image.equal_widths(*images):
                    self.file_manager.write(1, images[0], ext)
            if i != 1:
                self.file_manager.write(i, content, ext)

        self.file_manager.close()
        return True

    def download_episode(self, episode: int) -> bool:
        urls = self.scraper.get_url_images_episode(episode)
        for _ in range(self.retries):
            if is_downloaded := self.attempt_download_episode(episode, urls):
                break
            self.file_manager.delete(episode)
            sleep(self.time_between_retries)
        self.log.add(
            "download_episode",
            is_downloaded,
            episode=episode,
            urls=len(urls),
            referer=self.scraper.REFERER,
        )
        return is_downloaded

    def download_all(self) -> None:
        for episode in self.get_missing_episodes():
            self.download_episode(episode)
