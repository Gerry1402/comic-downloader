from collections.abc import Collection, Iterator

from rich.console import Console
from rich.table import Table

from core.comic import Comic
from core.scraper import Scraper
from data.data import Data
from utils.utils import reorder


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

    def sort_by(self, *keys: str) -> "Library":
        sorted_data = sorted(self._data, key=lambda c: tuple(c[key] for key in keys))
        return Library(sorted_data)

    def filter_by(self, **kwargs: str | bool | Collection) -> "Library":
        def check(c: dict) -> bool:
            return all(
                (c[k] in v if isinstance(v, Collection) else c[k] == v)
                for k, v in kwargs.items()
            )

        return Library([c for c in self._data if check(c)])

    def reorder(self, *keys: str) -> "Library":
        return Library(reorder(self._data, *keys))

    def show(self) -> None:
        table = Table(title=self.table_name, expand=True, row_styles=["", "on grey15"])

        for i, (column, options) in enumerate(self.table_columns.items(), start=1):
            table.add_column(
                column.capitalize(), ratio=1 if i == 1 else None, **options
            )

        def add_value(value: bool | str | int | float) -> str:
            if isinstance(value, bool):
                return self.emoji[int(value)]
            return str(value)

        for comic in self._data:
            table.add_row(*[add_value(comic[column]) for column in self.table_columns])

        Console().print(table)

    def __iter__(self) -> Iterator[tuple[Comic, Scraper]]:
        for comic in self._data:
            scraper = Scraper.sources[comic["source"]]
            yield Comic(**comic), scraper

    def __len__(self) -> int:
        return len(self._data)
