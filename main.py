from typing import Generator

from rich import pretty

from core.downloader import Downloader
from core.library import Library
from core.pipeline import Pipeline
from core.logger import Logger
from sources import load_all_modules


def get_library() -> Library:
    completed = False
    sources = ("asura", "webtoon")
    return Library().shuffle().filter_by(completed=completed, source=sources).reorder("source")


def get_comics() -> Generator[Downloader, None, None]:
    for scraper in get_library():
        yield scraper


def main() -> None:
    pretty.install()
    load_all_modules()
    Logger.setup()
    logger = Logger.logger()
    logger.info("Starting the comic downloader...")
    Pipeline(get_library()).run()
    logger.info("Finished downloading all comics.")


if __name__ == "__main__":
    main()
