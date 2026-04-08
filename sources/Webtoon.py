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
    DECREMENT: set[str] = {"Tower of God"}

    def missing_episodes(self) -> int:
        last_episode = get_elements_html(self.get_comic_html(), *self.LAST_EPISODE_CSS, first=True)
        last_episode = int(last_episode) - int(self.title in self.DECREMENT)
        return set(range(1, last_episode + 1)) - self.downloaded()

    def get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        return [url.split("?")[0] for url in get_elements_html(html, *self.IMAGES_CSS)]

    # def get_images_url_episode(self, episode: int) -> list[str]:

    #     incr = int(self.title == "Tower of God" and episode > 220)  # noqa: PLR2004
    #     html = get_html_parsed(self.url_episode(episode + incr), cookies=self.get_cookies())
    #     images = [url.split("?")[0] for url in get_elements_html(html, *self.IMAGES_CSS)]
    #     return images
