from sources.Comic import Comic
from utils.scraper import get_elements_html, get_html_parsed


class Webtoon(Comic):
    PATTERNS: dict[str, str] = {
        "series": "https://www.webtoons.com/a/a/a/list?title_no={comic_id}&page=1",
        "episode": "https://www.webtoons.com/en/a/a/a/viewer?title_no={comic_id}&episode_no={episode}",
    }
    IMAGES_CSS: tuple[str, str] = ("#_imageList img", "data-url")
    LAST_EPISODE_CSS: tuple[str, str] = ("li._episodeItem", "data-episode-no")
    REFERER: str = "https://www.webtoons.com/en/"
    COMPRESSION: bool = True

    def get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return get_elements_html(html, *self.IMAGES_CSS)
