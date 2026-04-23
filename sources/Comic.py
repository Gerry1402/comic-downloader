from datetime import datetime
from pathlib import Path
from time import sleep
from zipfile import ZIP_STORED, ZipFile

from selectolax.parser import HTMLParser

from config import get_settings
from data.data import get_data_as_dict
from utils.compress import equal_widths, transform_image
from utils.scraper import _content_image, get_elements_html, get_extension, get_html_parsed
from utils.utils import add_log, images_process, json_dump, json_load, sanitizing_title


class Comic:
    # BASE_PATH: Path = Path().home() / "Documents" / "Comics"
    BASE_PATH: Path = get_settings().base_path
    data: dict[str, tuple[str | int, str]] = get_data_as_dict()
    sources: dict[str, type["Comic"]] = {}
    z_fill: int = 4
    cookies: dict[str, str] = get_settings().model_dump(exclude={"base_path"})
    dates: dict[str, str] = json_load(Path(__file__).parent.parent / "data" / "dates.json")
    CORRECT_EP = {"Tower of God": {221: 1}}
    RETRIES = 3

    def __init__(self, title: str) -> None:
        self.title = title
        self.name = sanitizing_title(title)
        self.completed = self.data.get(title, [None])[-1]
        self.id = self.data.get(title, [None])[0]
        if self.id is None:
            raise KeyError(f'Comic "{title}" is not registered')
        self._comic_html = None
        self.errors = set()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        Comic.sources[cls.__name__.lower()] = cls

    @classmethod
    def create(cls, title: str) -> "Comic":
        source = cls.data.get(title, (None, None))[1]
        source_class = cls.sources.get(source)

        if source_class is None:
            raise KeyError(f'Source for "{title}" not found')

        return source_class(title)

    def path(self, *args: str) -> Path:
        path = self.BASE_PATH / self.name
        path.mkdir(parents=True, exist_ok=True)
        add_path = [str(arg).zfill(self.z_fill) for arg in args if arg or arg == 0]
        if len(add_path) != len(args):
            raise ValueError("Argument cannot be empty")
        return path.joinpath(*add_path)

    def downloaded(self) -> set[int]:
        return {int(file.stem) for file in self.path().rglob("*.cbz")} or {0}

    def _get_cookies(self) -> str:
        return self.cookies.get(self.__class__.__name__.lower(), "")

    def _adjust_ep(self, episode: int) -> int:
        data = self.CORRECT_EP.get(self.title, {})
        _, v = min(((e, v) for e, v in data.items() if episode >= e), key=lambda x: x[0], default=(-1, 0))
        return v

    def url_comic(self) -> str:
        return self.PATTERNS["series"].format(comic_id=self.id)

    def url_episode(self, episode: int) -> str:
        adjustment = self._adjust_ep(episode)
        return self.PATTERNS["episode"].format(comic_id=self.id, episode=episode + adjustment)

    def get_comic_html(self) -> HTMLParser:
        if self._comic_html is None:
            self._comic_html = get_html_parsed(self.url_comic())
        return self._comic_html

    def missing_episodes(self) -> set[int]:
        last_episode = get_elements_html(self.get_comic_html(), *self.LAST_EPISODE_CSS, first=True)
        last_episode = int(last_episode) - self._adjust_ep(int(last_episode))
        return set(range(1, last_episode + 1)) - self.downloaded()

    def get_url_images_episode(self, episode: int) -> list[str]:
        raise NotImplementedError("Method get_url_images_episode must be implemented in subclass")

    def _get_image_content(self, url: str) -> tuple[bytes, str]:
        content = _content_image(url.split("?", maxsplit=1)[0], self.REFERER, self._get_cookies())
        if self.COMPRESSION:
            content = transform_image(content)
        return content, ".webp" if self.COMPRESSION else get_extension(url)

    def download_episode(
        self,
        episode: int | float,
        workers: int = 15,
    ) -> bool:
        self._print(("status", f"Searching episode {episode}..."))
        urls = self.get_url_images_episode(episode)
        self._print(("status", f"Downloading episode {episode}..."))

        compare_content = [None, None]
        with ZipFile(self.path(episode).with_suffix(".cbz"), "w", compression=ZIP_STORED) as cbz_f:

            def write_image_indexed(i: int, content: bytes, ext: str) -> None:
                with cbz_f.open(f"{i:03}{ext}", "w") as f:
                    f.write(content)

            for i, (content, ext) in images_process(self._get_image_content, urls, workers):
                if content is None:
                    return False
                if i in (1, 2):
                    compare_content[i - 1] = content
                    if i == 1:
                        continue
                write_image_indexed(i, content, ext)
            if equal_widths(*compare_content):
                write_image_indexed(1, compare_content[0], ext)

        self.dates[self.name] = datetime.now().isoformat()
        json_dump(self.dates, Path(__file__).parent.parent / "data" / "dates.json")
        return True

    def download_all(self, workers: int = 15) -> None:
        self._print(("status", "Searching missing episodes..."))
        episode_status = ("error", "done")
        for episode in self.missing_episodes():
            for _ in range(self.RETRIES):
                if is_downloaded := self.download_episode(episode, workers):
                    break
                self.path(episode).with_suffix(".cbz").unlink(missing_ok=True)
                sleep(8)
            if not is_downloaded:
                self.errors.add(episode)
            add_log(episode_status[int(is_downloaded)], self.title, episode)
        self._print(("status", "Downloaded"), ("errors", len(self.errors)), end="\n")

    def _print(self, *args: tuple[str, str], end: str = "") -> None:
        content = ", ".join(f"{key}: {value}" for key, value in args)
        print(f"\r\033[K{self.title} -> (source: {self.__class__.__name__},  {content})", end=end)

    def __repr__(self) -> str:
        return f"{self.title} -> (source: {self.__class__.__name__},  path: {self.path()})"

    def __str__(self) -> str:
        return self.__repr__()
