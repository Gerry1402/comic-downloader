from pathlib import Path
from typing import Any

from curl_cffi import requests
from selectolax.parser import HTMLParser, Node


def get_html_parsed(url: str, cookies: str = "") -> HTMLParser:
    args: dict[str, Any] = {"url": url}
    if cookies:
        args["cookies"] = cookies
    response = requests.get(**args)
    if response.status_code != 200:  # noqa: PLR2004
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return HTMLParser(response.text)


def _content_image(url: str, referer: str, cookies: str = "") -> None:
    response = requests.get(
        url,
        cookies=cookies if cookies else None,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",  # noqa: E501
            "Referer": referer,
        },
    )
    if response.status_code != 200:  # noqa: PLR2004
        raise Exception(f"Failed to fetch image: {response.status_code}")
    return response.content


def get_extension(url: str) -> str:
    extensions = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "tiff",
        "tif",
        "webp",
        "svg",
        "ico",
        "heic",
        "heif",
        "avif",
        "jfif",
        "pjpeg",
        "pjp",
        "apng",
    }
    extension = url.split("?", maxsplit=1)[0].rsplit(".", maxsplit=1)[-1]
    return "." + extension if extension in extensions else "png"


def save_image(url: str, path: Path, cookies: str = "", referer: str = "") -> None:
    content = _content_image(url, referer, cookies)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(get_extension(url)).open("wb") as f:
        f.write(content)


def get_elements_html(
    html: HTMLParser,
    selector: str,
    attributes: str | list[str] | None = None,
    first: bool = False,
    filter: tuple[str, str] = (None, None),
) -> list[str | dict | Node] | str | dict | Node:

    results = []
    nodes = html.css(selector)
    if not nodes:
        # path = Path(__file__).parent.parent / "debugs" / "debug.html"
        # add_file(path, html.html)
        raise Exception(f"No elements found for selector: {selector}")
    for node in nodes:
        if isinstance(attributes, str):
            result = node.attributes.get(attributes)
        elif isinstance(attributes, list):
            result = {attr: node.attributes.get(attr) for attr in attributes}
        else:
            result = node
        results.append(result)
        if first:
            return results[0]
        if filter[0] is not None and filter[1] is not None and node.attributes.get(filter[0], "") == filter[1]:
            return results[-1]
    return results
