from selectolax.parser import HTMLParser

from config import get_settings
from core.comic import Comic
from core.image import Image
from core.logger import Logger
from core.url_builder import URLBuilder
from utils.scraper import _content_image, get_elements_html, get_extension, get_html_parsed


class Scraper(URLBuilder):
    cookies: dict[str, str] = get_settings().model_dump(exclude={"base_path"})
    sources: dict[str, type["Scraper"]] = {}

    def __init__(self, comic: Comic) -> None:
        super().__init__(comic)
        self._comic_html: HTMLParser | None = None
        self.avalaible_episodes: set[int] | None = None
        self.logger: Logger = Logger("scrape", comic)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        Scraper.sources[cls.__name__.lower()] = cls

    def get_cookies(self) -> str:
        return self.cookies.get(self.__class__.__name__.lower(), "")

    def get_comic_html(self) -> HTMLParser:
        if self._comic_html is None:
            error = False
            try:
                self._comic_html = get_html_parsed(self.url_comic())
            except Exception as e:
                error = str(e)
                raise (error)
            finally:
                self.logger.add("comic_html", bool(error), url=self.url_comic(), error=error)
        return self._comic_html

    def get_avalaible_episodes(self) -> set[int]:
        if self.avalaible_episodes is None:
            last_episode = int(get_elements_html(self.get_comic_html(), *self.LAST_EPISODE_CSS, first=True))
            final_episode = last_episode - len(self.skip.get(self.comic.title, set()))
            self.avalaible_episodes = set(range(1, final_episode + 1))
        return self.avalaible_episodes

    def _get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return get_elements_html(html, *self.IMAGES_CSS)

    def get_url_images_episode(self, episode: int) -> list[str]:
        urls = self._get_url_images_episode(episode)
        self.logger.add("url_images_episode", urls == [], episode=episode, url=self.url_episode(episode))
        return [url.split('?', 1)[0] for url in urls]

    def _get_image_content(self, url: str) -> tuple[bytes, str]:
        content = _content_image(url.split("?", maxsplit=1)[0], self.REFERER, self.get_cookies())
        if self.COMPRESSION:
            content = Image.transform_image(content)
        return content, ".webp" if self.COMPRESSION else get_extension(url)
