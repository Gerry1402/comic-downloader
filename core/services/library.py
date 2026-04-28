from collections.abc import Collection, Iterator
from random import shuffle
from typing import Any

from rich.console import Console
from rich.table import Table

from core.logging.logger import Logger
from core.models.comic import Comic
from core.scrapers.base import Scraper
from data.data import Data
from utils.utils import reorder

logger = Logger.logger()


class Library:
    data: list[dict] = Data.get_data()
    emoji: tuple[str, str] = ("[red]✖[/]", "[green]✔[/]")
    table_name: str = "Comic Library"
    table_columns: dict[str, dict[str, str | int]] = {
        "title": {"style": "bold"},
        "source": {"style": "cyan"},
        "completed": {"justify": "center"},
    }

    def __init__(self, data: list[dict] | None = None) -> None:
        self._data = data if data is not None else self.data.copy()

    def shuffle(self) -> "Library":
        logger.debug("Shuffling the library")
        data = self._data.copy()
        shuffle(data)
        return Library(data)

    def sort_by(self, *keys: str) -> "Library":
        logger.debug(f"Sorting the library by keys: {keys}")
        sorted_data = sorted(self._data, key=lambda c: tuple(c[key] for key in keys))
        return Library(sorted_data)

    def filter_by(self, **kwargs: str | bool | Collection) -> "Library":
        logger.debug(f"Filtering the library with criteria: {kwargs}")

        def check(c: dict) -> bool:
            return all((c[k] in v if isinstance(v, Collection) else c[k] == v) for k, v in kwargs.items())

        return Library([c for c in self._data if check(c)])

    def reorder(self, *keys: str) -> "Library":
        logger.debug(f"Reordering the library by keys: {keys}")
        return Library(reorder(self._data, *keys))

    def show(self) -> None:
        table = Table(title=self.table_name, expand=True, row_styles=["", "on grey15"])

        for i, (column, options) in enumerate(self.table_columns.items(), start=1):
            table.add_column(column.capitalize(), ratio=1 if i == 1 else None, **options)

        def add_value(value: bool | str | int | float) -> str:
            if isinstance(value, bool):
                return self.emoji[int(value)]
            return str(value)

        for comic in self._data:
            table.add_row(*[add_value(comic[column]) for column in self.table_columns])

        Console().print(table)

    @classmethod
    def get(cls, title: str, default: Any | None = None) -> Scraper:
        for comic in cls.data:
            if comic["title"] == title:
                scraper = Scraper.sources[comic["source"]]
                return scraper(Comic(**comic))
        raise KeyError(f"Comic with title '{title}' not found in library.")

    def __iter__(self) -> Iterator[Scraper]:
        for comic in self._data:
            scraper = Scraper.sources[comic["source"]]
            yield scraper(Comic(**comic))

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: str | Comic) -> bool:
        if isinstance(item, str):
            return any(c["title"] == item for c in self._data)
        elif isinstance(item, Comic):
            return any(c["title"] == item.title for c in self._data)
        return False

    def __getitem__(self, title: str) -> Scraper:
        for comic in self._data:
            if comic["title"] == title:
                scraper = Scraper.sources[comic["source"]]
                return scraper(Comic(**comic))
        raise KeyError(f"Comic with title '{title}' not found in library.")
