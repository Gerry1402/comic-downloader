from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Collection, Generator, TypeVar

T = TypeVar("T")


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


def reorder_by_frequency(
    data: list[dict],
    key: str,
) -> list[dict]:
    n_data = len(data)
    counts = Counter(item[key] for item in data)
    next_time = dict.fromkeys(counts, 0.0)
    step = {key: n_data / count for key, count in counts.items()}

    main_key = {}
    for item in data:
        main_key.setdefault(item[key], []).append(item)

    new_data = []
    for _ in range(n_data):
        avalaible_key_values = {key for key, values in main_key.items() if values}
        key_value = min(avalaible_key_values, key=lambda c: (next_time[c], -len(main_key[c])))
        new_data.append(main_key[key_value].pop(0))
        next_time[key_value] += step[key_value]
    return new_data

def reorder(data: list[dict], *keys: str) -> list[dict]:
    if not keys or not data:
        return list(data)

    groups: dict = {}
    for item in data:
        groups.setdefault(item[keys[0]], []).append(item)

    for k, values in groups.items():
        groups[k] = reorder(values, *keys[1:])

    flat = [item for group in groups.values() for item in group]
    return reorder_by_frequency(flat, keys[0])


def threadpool(
    function: Callable,
    *args: Collection,
    workers: int,
) -> Generator[Any, None, None]:

    if len({len(arg) for arg in args}) != 1:
        raise ValueError("All arguments must have the same length.")

    parameters = zip(*args)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(function, *params): i for i, params in enumerate(parameters, start=1)}
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception:
                result = None
            finally:
                yield (futures[future], result)
