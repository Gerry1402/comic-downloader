import contextlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Generator


def json_dump(data: dict | list, path: Path | str) -> None:
    with Path(path).with_suffix(".json").open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)


def json_load(path: Path | str) -> dict | list:
    try:
        with Path(path).with_suffix(".json").open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        json_dump({}, Path(path).with_suffix(".json"))
        return {}


def sanitizing_title(title: str) -> str:
    replacements = {
        "?": "ʔ",
        "*": "⋆",
        "<": "‹",
        ">": "›",
        "–": "-",
        ":": "꞉",
        "\\": "＼",
        "/": "／",
        "\u200b": "",
    }
    name = " ".join(title.strip().split())
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def add_log(name: str, title: str, episode: int) -> None:
    data = json_load(name)
    if episode not in data.get(title, []):
        episodes = data.setdefault(title, [])
        episodes.append(episode)
        data[title] = sorted(set(episodes))
        json_dump(data, Path(name))


def add_file(name: str | Path, content: str) -> None:
    path = Path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    index = 0
    while path.exists():
        index += 1
        path = path.with_stem(path.stem.split("_")[0] + f"_{index:02}")
    with path.open("w", encoding="utf-8") as f:
        f.write(content + "\n")


def episode_process(function: Callable, episodes: list[int]) -> Generator[Any, None, None]:

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(function, episode): episode for episode in episodes}
        for future in as_completed(futures):
            with contextlib.suppress(Exception):
                yield futures[future], future.result()


def images_process(
    function: Callable,
    images_urls: list[str],
    workers: int,
) -> Generator[Any, None, None]:

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(function, url): (i, url) for i, url in enumerate(images_urls, start=1)}
        for future in as_completed(futures):
            try:
                result = future.result()
                yield (futures[future][0], result)
            except Exception:
                yield (futures[future][0], (None, None))
