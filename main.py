from core.downloader import Downloader
from core.library import Library
from sources import load_all_modules

load_all_modules()


def get_comics() -> None:
    completed = False
    source = ("asura", "webtoon")
    library = Library().filter_by(completed=completed, source=source).reorder_by_source()
    for comic, scraper in library:
        downloader = Downloader(comic, scraper)
        if downloader.get_missing_episodes():
            downloader.download_all()


def main() -> None:
    get_comics()


if __name__ == "__main__":
    main()
