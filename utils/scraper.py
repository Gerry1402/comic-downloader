from typing import Any

from curl_cffi import requests
from selectolax.parser import HTMLParser, Node

from core import Logger

logger = Logger.logger()


def clean_url(url: str) -> str:
    return url.split("?", 1)[0]


def get_html_parsed(url: str, cookies: str = "") -> HTMLParser:
    logger.debug("Fetching HTML content", extra={"url": url})
    kwargs: dict[str, Any] = {"url": url}
    if cookies:
        kwargs["cookies"] = cookies
    response = requests.get(**kwargs)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return HTMLParser(response.text)


def content_image(url: str, referer: str, cookies: str = "") -> bytes:
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
    return "." + (extension if extension in extensions else "png")


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
        html.strip_tags(["head", "script", "style"])
        with Logger.files.directory.joinpath("debug.html").open("w", encoding="utf-8") as f:
            f.write(html.html)
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
