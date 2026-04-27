from selectolax.parser import HTMLParser

from config import get_settings
from core.comic import Comic
from core.image import Image
from core.logger import Logger
from core.url_builder import URLBuilder
from utils.scraper import (
    content_image,
    get_elements_html,
    get_extension,
    get_html_parsed,
)

logger = Logger.logger()


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
        extra = self.comic.logger(url=self.url_comic())
        if self.available_episodes is None:
            logger.debug("Getting available episodes", **extra)
            try:
                logger.debug("Parsing the last episode", **extra)
                last_episode = get_elements_html(self.get_comic_html(), *self.LAST_EPISODE_CSS, first=True)
            except Exception:
                logger.error("Failed to parse the last episode", **extra)
                raise RuntimeError("Failed to parse the last episode")
            try:
                logger.debug("Converting the last episode to int", **extra)
                last_episode = int(last_episode)
            except ValueError:
                logger.error("Failed to convert the last episode to int", **extra)
                raise RuntimeError("Failed to convert the last episode to int")
            final_episode = last_episode - self.adjustment_episode(last_episode)
            self.available_episodes = set(range(1, final_episode + 1))
        return self.available_episodes

    def _get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return get_elements_html(html, *self.IMAGES_CSS)

    def get_url_images_episode(self, episode: int) -> list[str]:
        extra = self.comic.logger(url=self.url_episode(episode), episode=episode)
        logger.debug(f"Getting image URLs for episode {episode}", **extra)
        urls = self._get_url_images_episode(episode)
        if not urls:
            logger.error(f"No image URLs found for episode {episode}", **extra)
            raise RuntimeError(f"No image URLs found for episode {episode}")
        return [url.split("?", 1)[0] for url in urls]

    def _get_image_content(self, url: str) -> tuple[bytes, str]:
        content = content_image(url.split("?", maxsplit=1)[0], self.REFERER, self.get_cookies())
        if self.COMPRESSION:
            content = Image.transform_image(content)
        return content, ".webp" if self.COMPRESSION else get_extension(url)
