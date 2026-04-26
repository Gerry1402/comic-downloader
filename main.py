from typing import Generator

from core.downloader import Downloader
from core.library import Library
from core.pipeline import Pipeline
from sources import load_all_modules

load_all_modules()

def get_library() -> Library:
    completed = False
    sources = ("asura", "webtoon")
    return Library().shuffle().filter_by(completed=completed, source=sources).reorder("source")


def get_comics() -> Generator[Downloader, None, None]:
    for scraper in get_library():
        yield scraper


def main() -> None:
    Pipeline(get_library()).run()


if __name__ == "__main__":
    main()
