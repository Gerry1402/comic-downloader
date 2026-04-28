import json
from typing import Generator

from core.scraper import Scraper
from utils.scraper import get_elements_html, get_html_parsed


def clean(string: str, key: str) -> Generator[dict, None, None]:
    data = json.loads(string).get(key, [None, []])[1]

    def clean_metadata(content: dict | list | str | int | float | bool) -> dict:
        new_content = {}
        if isinstance(content, dict):
            for k, v in content.items():
                new_content[k] = clean_metadata(v)
            return new_content
        elif isinstance(content, list):
            return clean_metadata(content[1])
        else:
            return content

    for item in data:
        yield clean_metadata(item)


class Asura(Scraper):
    PATTERNS: dict[str, str] = {
        "series": "https://asurascans.com/comics/{comic_id}-26f76d6d",
        "episode": "https://asurascans.com/comics/{comic_id}-26f76d6d/chapter/{episode}",
    }
    IMAGES_CSS: tuple[str, str] = (".select-none img", "src")
    LAST_EPISODE_CSS: tuple[str, str] = ("metadata", "metadata")
    REFERER: str = "https://asurascans.com/"
    METADATA_CSS: tuple[str, str] = ("astro-island", "props")
    COMPRESSION: bool = False

    def _get_available_episodes(self) -> set[int]:
        data = get_elements_html(self.get_comic_html(), *self.METADATA_CSS, filter=("prefix", "r22"))
        return {int(item["number"]) for item in clean(data, "chapters") if not item.get("is_locked")}

    def _get_url_images_episode(self, episode: int) -> list[str]:
        html = get_html_parsed(self.url_episode(episode))
        data = get_elements_html(html, *self.METADATA_CSS, filter=("prefix", "r1"))
        return [item["url"] for item in clean(data, "pages")]
