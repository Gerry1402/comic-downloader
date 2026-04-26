from typing import Generator

from core.comic import Comic
from core.downloader import Downloader
from core.library import Library
from sources import load_all_modules
from utils.utils import reorder

load_all_modules()


def get_comics() -> Generator[Downloader, None, None]:
    completed = False
    sources = ("asura", "webtoon")
    library = Library().filter_by(completed=completed, source=sources).reorder("source")
    # print(len(library))
    # print(len(library))
    for comic, scraper in library:
        yield Downloader(comic, scraper)


def get_missing_episodes() -> list[dict[str, str | Comic | Downloader | int]]:

    def convert(d: Downloader, e: int) -> dict[str, str | Comic | Downloader | int]:
        return {
            "source": d.comic.source,
            "comic": d.comic,
            "downloader": d,
            "episode": e,
        }

    data: list[dict] = [
        convert(d, e) for d in get_comics() for e in d.get_missing_episodes()
    ]
    return reorder(data, "source", "comic")[:1]


def main() -> None:
    for downloader in get_comics():
        downloader.download_all()


if __name__ == "__main__":
    main()
