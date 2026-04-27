from dataclasses import dataclass, field

from utils.utils import sanitizing_title


@dataclass(frozen=True)
class Comic:
    title: str
    name: str = field(init=False)
    source: str
    id: str
    completed: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", sanitizing_title(self.title))

    def to_dict(self) -> dict[str, str | bool]:
        return self.__dict__

    def logger(self, **kwargs: str | bool | int | float) -> dict[str, str | bool | int | float]:
        return {"extra": {"source": self.source.capitalize(), "title": self.title, **kwargs}}

    def __repr__(self) -> str:
        content = self.to_dict()
        content.pop("title")
        return f"{self.title} ({', '.join(f'{k}={v}' for k, v in content.items())})"

    def __str__(self) -> str:
        return f"{self.source.capitalize()} · {self.title}"
