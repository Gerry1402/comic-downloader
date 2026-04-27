from time import sleep

from core.comic import Comic
from core.file_manager import FileManager
from core.image import Image
from core.logger import Logger
from core.scraper import Scraper
from utils.utils import threadpool

logger = Logger.logger()


class Downloader:
    retries: int = 3
    time_between_retries: int = 8
    workers: int = 15

    def __init__(self, scraper: Scraper) -> None:
        self.comic: Comic = scraper.comic
        self.scraper: Scraper = scraper
        self.file_manager: FileManager = FileManager(self.comic)

    def get_missing_episodes(self) -> set[int]:
        logger.info("Checking for missing episodes", **self.comic.logger(url=self.scraper.url_comic()))
        available = self.scraper.get_available_episodes()
        downloaded = self.file_manager.get_downloaded_episodes()
        if max(available) == max(downloaded):
            logger.info("Comic is updated", **self.comic.logger(url=self.scraper.url_comic()))
        elif max(downloaded) > max(available):
            logger.warning(
                f"More downloaded episodes ({max(downloaded)}) than available ({max(available)})",
                **self.comic.logger(url=self.scraper.url_comic()),
            )
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
                if all(images):
                    if Image.equal_widths(*images):
                        self.file_manager.write(1, images[0], ext)
                    else:
                        logger.warning(
                            "The first two images have different widths",
                            **self.comic.logger(url=self.scraper.url_episode(episode), episode=episode),
                        )
            if i != 1:
                self.file_manager.write(i, content, ext)

        self.file_manager.close()
        return True

    def download_episode(self, episode: int) -> bool:
        extra = self.comic.logger(url=self.scraper.url_episode(episode), episode=episode)
        logger.info(f"Downloading episode {episode}", **extra)
        urls = self.scraper.get_url_images_episode(episode)
        for i in range(1, self.retries + 1):
            logger.debug(f"Attempt {i} to download episode {episode}", **extra)
            if is_downloaded := self.attempt_download_episode(episode, urls):
                logger.info(f"Successfully downloaded episode {episode} on attempt {i}", **extra)
                break
            logger.warning(f"Failed to download episode {episode} on attempt {i}", **extra)
            self.file_manager.delete(episode)
            logger.debug(f"Waiting {self.time_between_retries} seconds", **extra)
            sleep(self.time_between_retries)
        if is_downloaded:
            logger.info(f"Finished downloading episode {episode}", **extra)
        else:
            logger.error(f"Failed to download episode {episode}", **extra)
        return is_downloaded

    def download_all(self) -> None:
        logger.info("Starting download of missing episodes", **self.comic.logger(url=self.scraper.url_comic()))
        for episode in self.get_missing_episodes():
            self.download_episode(episode)
        logger.info("Finished downloading episodes", **self.comic.logger(url=self.scraper.url_comic()))
