from selectolax.parser import HTMLParser

from config import get_settings
from core.comic import Comic
from core.image import Image
from core.url_builder import URLBuilder
from utils.scraper import (
    content_image,
    get_elements_html,
    get_extension,
    get_html_parsed,
)


class Scraper(URLBuilder):
    cookies: dict[str, str] = get_settings().model_dump(exclude={"base_path"})
    sources: dict[str, type["Scraper"]] = {}

    def __init__(self, comic: Comic) -> None:
        super().__init__(comic)
        self._comic_html: HTMLParser | None = None
        self.available_episodes: set[int] | None = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        Scraper.sources[cls.__name__.lower()] = cls

    def get_cookies(self) -> str:
        return self.cookies.get(self.__class__.__name__.lower(), "")

    def get_comic_html(self) -> HTMLParser:
        if self._comic_html is None:
            self._comic_html = get_html_parsed(self.url_comic())
        return self._comic_html

    def get_available_episodes(self) -> set[int]:
        if self.available_episodes is None:
            last_episode = int(get_elements_html(self.get_comic_html(), *self.LAST_EPISODE_CSS, first=True))
            final_episode = last_episode - len(self.skip.get(self.comic.title, set()))
            self.available_episodes = set(range(1, final_episode + 1))
        return self.available_episodes

    def _get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return get_elements_html(html, *self.IMAGES_CSS)

    def get_url_images_episode(self, episode: int) -> list[str]:
        urls = self._get_url_images_episode(episode)
        return [url.split("?", 1)[0] for url in urls]

    def _get_image_content(self, url: str) -> tuple[bytes, str]:
        content = content_image(url.split("?", maxsplit=1)[0], self.REFERER, self.get_cookies())
        if self.COMPRESSION:
            content = Image.transform_image(content)
        return content, ".webp" if self.COMPRESSION else get_extension(url)
