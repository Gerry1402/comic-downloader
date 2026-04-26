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
        return f"{self.title} (name={self.name}, source={self.source}, id={self.id}, completed={self.completed})"

    def __str__(self) -> str:
        return self.__repr__()
