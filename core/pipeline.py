from __future__ import annotations

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Column

from core.downloader import Downloader
from core.logger import Logger
from core.library import Library
from utils.utils import reorder

logger = Logger.logger()


class Pipeline:
    console: Console = Console()

    def __init__(self, library: Library) -> None:
        self.library = library
        self.episodes: list[dict[str, str | int]] = []

    def _build_progress(self, spinner: bool, **kwargs: bool) -> Progress:
        data = (
            SpinnerColumn(),
            TextColumn(
                "{task.description}",
                table_column=Column(
                    ratio=1,
                    overflow="ellipsis",
                    no_wrap=True,
                ),
            ),
            BarColumn(),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
        )
        return Progress(*data[0 if spinner else 1 :], console=self.console, **kwargs)

    def collect(self) -> None:
        
        with self._build_progress(True, expand=True, transient=True) as spinner:
            task = spinner.add_task("", total=len(self.library))
            for scraper in self.library:
                spinner.update(task, description=f'Searching "{scraper.comic.title}"...')
                eps = Downloader(scraper).get_missing_episodes()
                self.episodes += [{**scraper.comic.to_dict(), "episode": ep} for ep in eps]
                spinner.advance(task)
        self.episodes = reorder(self.episodes, "source", "title")

    def run(self) -> None:
        self.collect()

        with self._build_progress(False, expand=True, transient=False) as progress:
            task = progress.add_task("", total=len(self.episodes))
            for ep in self.episodes:
                progress.update(
                    task,
                    description=f"{ep['source']} · {ep['title']} · Downloading {ep['episode']}...",
                )
                Downloader(Library.get(ep["title"])).download_episode(ep["episode"])
                progress.advance(task)
