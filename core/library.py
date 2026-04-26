from collections.abc import Collection, Iterator

from core.comic import Comic
from core.scraper import Scraper
from data.data import Data
from utils.utils import reorder_by_frequency


class Library:
    data: list[dict] = Data.get_data()

    def __init__(self, data: list[dict] | None = None) -> None:
        self._data = data if data is not None else self.data.copy()

    def sort_by(self, *keys: str) -> "Library":
        sorted_data = sorted(self._data, key=lambda c: tuple(c[key] for key in keys))
        return Library(sorted_data)

    def filter_by(self, **kwargs: str | bool | Collection) -> "Library":
        def check(c: dict) -> bool:
            return all((c[k] in v if isinstance(v, Collection) else c[k] == v) for k, v in kwargs.items())

        return Library([c for c in self._data if check(c)])

    def reorder_by_source(self) -> "Library":
        return Library(reorder_by_frequency(self._data, "source"))

    def __iter__(self) -> Iterator[tuple[Comic, Scraper]]:
        for comic in self._data:
            scraper = Scraper.sources[comic["source"]]
            yield Comic(**comic), scraper
