from core import Scraper


class Rizz(Scraper):
    PATTERNS: dict[str, str] = {
        "series": "https://rizzfables.com/series/r2311170-{comic_id}",
        "episode": "https://rizzfables.com/chapter/r2311170-{comic_id}-chapter-{episode}",
    }
    IMAGES_CSS: tuple[str, str] = ("#readerarea img", "src")
    LAST_EPISODE_CSS: tuple[str, str] = ("#chapterlist li", "data-num")
    REFERER: str = "https://rizzfables.com/"
    COMPRESSION: bool = False
