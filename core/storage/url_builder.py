from core.models.comic import Comic


class URLBuilder:
    skip: dict[str, set[int]] = {"Tower of God": {221}}

    def __init__(self, comic: Comic) -> None:
        self.comic = comic

    def adjustment_episode(self, episode: int) -> int:
        return len([e for e in self.skip.get(self.comic.title, set()) if episode >= e])

    def url_comic(self) -> str:
        return self.PATTERNS["series"].format(comic_id=self.comic.id)

    def url_episode(self, episode: int) -> str:
        adjustment = self.adjustment_episode(episode)
        return self.PATTERNS["episode"].format(comic_id=self.comic.id, episode=episode + adjustment)
