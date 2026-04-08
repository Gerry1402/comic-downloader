import json

from sources.Comic import Comic
from utils.Browser import BrowserManager
from utils.scraper import get_elements_html


def clean_metadata(string: str) -> dict:
    data = json.loads(string)

    def clean(content: dict | list | str | int | float | bool) -> dict:
        new_content = {}
        if isinstance(content, dict):
            for key, value in content.items():
                new_content[key] = clean(value)
            return new_content
        elif isinstance(content, list):
            return clean(content[1])
        else:
            return content

    new_data = clean(data)
    new_data["chapters"] = [clean(chapter) for chapter in data.get("chapters", [None, None])[1]]
    return new_data


class Asura(Comic):
    PATTERNS: dict[str, str] = {
        "series": "https://asurascans.com/comics/{comic_id}-26f76d6d",
        "episode": "https://asurascans.com/comics/{comic_id}-26f76d6d/chapter/{episode}",
    }
    IMAGES_CSS: tuple[str, str] = (".select-none img", "src")
    REFERER: str = "https://asurascans.com/"
    METADATA: tuple[str, str, tuple[str, str]] = ("astro-island", "props", ("prefix", "r21"))
    COMPRESSION: bool = False

    def get_metadata(self) -> dict:
        html = self.get_comic_html()
        metadata = get_elements_html(html, self.METADATA[0], self.METADATA[1], filter=self.METADATA[2])
        return clean_metadata(metadata)

    def missing_episodes(self) -> set[int]:
        metadata = self.get_metadata()
        avalaible = {int(chapter["number"]) for chapter in metadata.get("chapters", []) if not chapter.get("is_locked")}
        return avalaible - self.downloaded()

    def get_url_images_episode(self, episode: int) -> list[str]:
        with BrowserManager() as browser:
            html = browser.fetch(self.url_episode(episode))
            return [url.split("?")[0] for url in get_elements_html(html, *self.IMAGES_CSS)]
