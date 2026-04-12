from itertools import zip_longest

from sources import load_all_modules
from sources.Comic import Comic

load_all_modules()


def get_available_comics() -> list[Comic]:
    data = Comic.data
    comics = {}
    for title in data:
        source = data[title][1]
        if source not in Comic.sources:
            continue
        comics.setdefault(source, []).append(Comic.create(title))
    return [c for g in zip_longest(*comics.values(), fillvalue=None) for c in g if c]


def main() -> None:
    comics = get_available_comics()
    for comic in comics:
        if comic.completed:
            continue
        comic.download_all()


if __name__ == "__main__":
    # comic = Comic.create("Jungle Juice")
    # comic = Comic.create("Tower of God")
    # comic = Comic.create("Overgeared")
    # print(comic.url_comic(), comic.get_metadata())
    # comic = Comic.create("Logging 10,000 Years into the Future")
    # comic.download_all()
    # comic.download_episode(197)
    # comic.download_all()
    # for comic in get_available_comics():
    #     print(comic.path())
    main()
