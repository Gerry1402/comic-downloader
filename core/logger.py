import logging
import logging.config
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Literal

from rich.logging import RichHandler


class ContextFormatter(logging.Formatter):
    def format(self, record):
        base = record.getMessage()

        fields = []
        for key in ("source", "title", "episode", "url", "images"):
            value = getattr(record, key, None)
            if value:
                fields.append(str(value))

        if fields:
            return f"{base} ( {' · '.join(fields)} )"
        return base


@dataclass(frozen=True)
class Rich:
    level: ClassVar[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = "WARNING"
    name: ClassVar[str] = "console"
    formatter_name: ClassVar[str] = "rich"
    format: ClassVar[ContextFormatter] = ContextFormatter
    tracebacks: ClassVar[bool] = True
    markup: ClassVar[bool] = True
    datefmt: ClassVar[str] = "[%H:%M:%S]"

    @classmethod
    def get_formatter(cls) -> dict[str, dict[str]]:
        return {cls.formatter_name: {"()": cls.format, "datefmt": cls.datefmt}}

    @classmethod
    def get_handler(cls) -> dict[str, str | bool | RichHandler]:
        return {
            cls.name: {
                "()": RichHandler,
                "level": cls.level,
                "formatter": cls.formatter_name,
                "rich_tracebacks": cls.tracebacks,
                "markup": cls.markup,
            }
        }


@dataclass(frozen=True)
class File:
    directory: ClassVar[Path] = Path(__file__).parent.parent / "logs"
    timestamp: ClassVar[str] = datetime.now().strftime("%Y-%m-%d")
    filename: ClassVar[str] = "{name}_{timestamp}.log"

    formatter_name: ClassVar[str] = "detailed"
    format: ClassVar[str] = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt: ClassVar[str] = "%Y-%m-%d %H:%M:%S"

    files: ClassVar[set["File"]] = set()

    name: str
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    def __post_init__(self):
        object.__setattr__(
            self, "path", self.directory / self.filename.format(name=self.name, timestamp=self.timestamp)
        )
        self.directory.mkdir(exist_ok=True)
        File.files.add(self)

    @classmethod
    def get_formatter(cls) -> dict[str, dict[str]]:
        return {cls.formatter_name: {"format": cls.format, "datefmt": cls.datefmt}}

    @classmethod
    def get_handlers(self) -> list[dict[str, dict[str, str]]]:
        return {
            self.name: {
                "class": "logging.FileHandler",
                "filename": str(self.path),
                "level": self.level,
                "formatter": self.formatter_name,
            }
            for self in File.files
        }


class Logger:
    name: str = "app"
    version: int = 1
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    propagate: bool = False
    files: list[tuple[str, str]] = [("app", "DEBUG"), ("error", "ERROR")]
    separator: str = " · "

    @classmethod
    def setup(cls):
        [File(name, level) for name, level in cls.files]
        logging.config.dictConfig(
            {
                "version": cls.version,
                "disable_existing_loggers": False,
                "formatters": {
                    **Rich.get_formatter(),
                    **File.get_formatter(),
                },
                "handlers": {
                    **Rich.get_handler(),
                    **File.get_handlers(),
                },
                "loggers": {
                    cls.name: {
                        "level": cls.level,
                        "handlers": list((File.get_handlers() | Rich.get_handler()).keys()),
                        "propagate": cls.propagate,
                    },
                },
            }
        )

    @classmethod
    def logger(cls) -> logging.Logger:
        return logging.getLogger(cls.name)
