from sources import load_all_modules
from sources.Comic import Comic

load_all_modules()


def get_available_comics() -> list[Comic]:
    data = Comic.data
    sources = Comic.sources
    return [Comic.create(title) for title in data if data[title][1] in sources]


def random_check_comics() -> None:
    comics = get_available_comics()
    for comic in comics:
        if comic.completed or comic.__class__.__name__.lower()!= "asura":
            continue
        comic.get_metadata()


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
