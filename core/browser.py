from typing import Self

from playwright.sync_api import Route, sync_playwright
from selectolax.parser import HTMLParser


def block_content(route: Route) -> None:
    if route.request.resource_type in ["image", "media", "font"]:
        route.abort()
    else:
        route.continue_()


class BrowserManager:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self) -> None:
        if self.browser is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()

    def fetch(self, url: str) -> HTMLParser:
        if self.browser is None:
            self.start()
        page = self.context.new_page()
        page.route("**/*", block_content)
        page.goto(url)
        previous_height = 0
        while True:
            page.wait_for_timeout(1500)
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height
            page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
        html = HTMLParser(page.content())
        page.close()
        return html

    def close(self) -> None:
        if self.browser:
            self.context.close()
            self.browser.close()
            self.playwright.stop()

            self.browser = None
            self.context = None
            self.playwright = None

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
