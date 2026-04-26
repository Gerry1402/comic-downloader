from typing import Generator

from core.comic import Comic
from core.downloader import Downloader
from core.library import Library
from sources import load_all_modules
from utils.utils import reorder

load_all_modules()


def get_comics() -> Generator[Downloader, None, None]:
    completed = False
    source = ("asura", "webtoon")
    library = Library().filter_by(completed=completed, source=source).reorder_by_source()
    for comic, scraper in library:
        yield Downloader(comic, scraper)


def get_missing_episodes() -> list[str]:

    def convert(d: Downloader, e: int) -> dict[str, str | Comic | Downloader | int]:
        return {"source": d.comic.source, "comic": d.comic, "downloader": d, "episode": e}

    data: list[dict] = [convert(d, e) for d in get_comics() for e in d.get_missing_episodes()]
    return reorder(data, "source", "comic")


def main() -> None:
    get_comics()


if __name__ == "__main__":
    main()
