from time import sleep

from rich.progress import BarColumn, Progress, TaskID, TaskProgressColumn, TextColumn

from core.comic import Comic
from core.file_manager import FileManager
from core.image import Image
from core.logger import Logger
from core.scraper import Scraper
from utils.utils import threadpool


class Downloader:
    retries: int = 3
    time_between_retries: int = 8
    len_text: int = 0

    def __init__(self, comic: Comic, scraper: Scraper) -> None:
        self.comic: Comic = comic
        self.scraper: Scraper = scraper(comic)
        self.file_manager: FileManager = FileManager(comic)
        self.status: str = "Initialized"
        self.log: Logger = Logger("download", comic)
        self.progress: Progress = Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )

    def get_missing_episodes(self) -> set[int]:
        avalaible = self.scraper.get_avalaible_episodes()
        downloaded = self.file_manager.get_downloaded_episodes()
        self.log.add(
            "missing_episodes",
            len(avalaible) < len(downloaded),
            comic_url=self.scraper.url_comic(),
        )
        return avalaible - downloaded - {0}

    def attempt_download_episode(
        self, episode: int, urls: list[str], workers: int, task_ep: TaskID | None = None
    ) -> bool:
        images: list[bytes | None, bytes | None] = [None, None]

        self.file_manager.open(episode)

        for i, result in threadpool(
            self.scraper._get_image_content, urls, workers=workers
        ):
            if result is None:
                self.file_manager.close()
                return False
            content, ext = result
            if not all(images):
                images[int(i != 1)] = content
                if all(images) and Image.equal_widths(*images):
                    self.file_manager.write(i, images[0], ext)
            if i != 1:
                self.file_manager.write(i, content, ext)
            self.progress.advance(task_ep)

        self.file_manager.close()
        return True

    def download_episode(
        self, episode: int | float, task_global: TaskID | None = None, workers: int = 15
    ) -> bool:
        urls = self.scraper.get_url_images_episode(episode)
        task_ep = (
            self.progress.add_task(f" · {episode}", total=len(urls))
            if task_global is not None
            else None
        )
        for _ in range(self.retries):
            if is_downloaded := self.attempt_download_episode(
                episode, urls, workers, task_ep
            ):
                break
            self.file_manager.path(episode).unlink(missing_ok=True)
            sleep(self.time_between_retries)
        if task_ep is not None:
            self.progress.remove_task(task_ep)
            self.progress.advance(task_global)
        self.log.add(
            "download_episode",
            is_downloaded,
            episode=episode,
            urls=len(urls),
            referer=self.scraper.REFERER,
        )

    def download_all(self, workers: int = 15) -> None:
        missing = self.get_missing_episodes()
        self.progress.start()
        task_global = self.progress.add_task(self.comic.title, total=len(missing))
        for episode in missing:
            self.download_episode(episode, task_global, workers)
        self.progress.stop()
