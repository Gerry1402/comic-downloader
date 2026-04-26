from dataclasses import dataclass, field

from utils.utils import sanitizing_title


@dataclass(frozen=True)
class Comic:
    title: str
    source: str
    id: str
    completed: bool
    name: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", sanitizing_title(self.title))

    def __repr__(self) -> str:
        content = self.__dict__.copy()
        content.pop("title")
        return f"{self.title} ({', '.join(f'{k}={v}' for k, v in content.items())})"

    def __str__(self) -> str:
        return self.__repr__()
