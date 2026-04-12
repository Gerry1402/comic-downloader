from sources.Comic import Comic
from utils.scraper import get_elements_html, get_html_parsed


class Rizz(Comic):
    PATTERNS: dict[str, str] = {
        "series": "https://rizzfables.com/series/r2311170-{comic_id}",
        "episode": "https://rizzfables.com/chapter/r2311170-{comic_id}-chapter-{episode}",
    }
    IMAGES_CSS: tuple[str, str] = ("#readerarea img", "src")
    LAST_EPISODE_CSS: tuple[str, str] = ("#chapterlist li", "data-num")
    REFERER: str = "https://rizzfables.com/"
    COMPRESSION: bool = False
    DECREMENT: set[str] = {}

    def missing_episodes(self) -> int:
        last_episode = get_elements_html(self._get_comic_html(), *self.LAST_EPISODE_CSS, first=True)
        return set(range(1, last_episode + 1)) - self.downloaded()

    def get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return [url.split("?")[0] for url in get_elements_html(html, *self.IMAGES_CSS)]
