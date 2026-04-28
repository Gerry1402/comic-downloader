# Comic Downloader

A modular Python tool that downloads comic and manhwa chapters from supported websites and packages each episode as a `.cbz` file, ready to open in any comic reader.

---

## Table of Contents

- [Comic Downloader](#comic-downloader)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [How It Works](#how-it-works)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [`.env.path` — download folder](#envpath--download-folder)
    - [`.env.cookies` — optional session cookies](#envcookies--optional-session-cookies)
  - [Managing your comic list](#managing-your-comic-list)
    - [data/data.xlsx structure](#datadataxlsx-structure)
    - [Adding a comic](#adding-a-comic)
  - [Running the downloader](#running-the-downloader)
  - [Output format](#output-format)
  - [Supported sources](#supported-sources)
  - [Adding a new source](#adding-a-new-source)
    - [Required class attributes](#required-class-attributes)
    - [Optional overrides](#optional-overrides)
  - [Episode numbering and skips](#episode-numbering-and-skips)
  - [Troubleshooting](#troubleshooting)

---

## Overview

Comic Downloader automates saving comics chapter by chapter. It reads a registry from `data/data.xlsx`, checks which episodes are already on disk, and downloads only the missing ones. Each episode is packaged as a `.cbz` archive (a ZIP file that any comic reader understands), with optional WEBP conversion to reduce file size.

The tool is built around a **plugin architecture**: every website is an independent *source* class. Adding support for a new site means writing one small Python file — no changes to the core are needed.

---

## Project Structure

```plaintext
comic-downloader/
├── config/
│   ├── __init__.py         # Re-exports Settings and get_settings
│   └── settings.py         # Typed settings loaded from .env files
├── main.py                 # Entry point
├── pyproject.toml
│
├── core/
│   ├── __init__.py         # Public API — re-exports all core classes
│   ├── logging/
│   │   └── logger.py       # Rich console + rotating file logging
│   ├── models/
│   │   ├── comic.py        # Comic dataclass
│   │   └── image.py        # WEBP image conversion
│   ├── scrapers/
│   │   ├── base.py         # Base Scraper (HTTP + HTML parsing + plugin registry)
│   │   └── browser.py      # Playwright browser for JS-heavy pages
│   ├── services/
│   │   ├── downloader.py   # Per-episode download logic with retries
│   │   ├── library.py      # Comic collection with filtering/sorting
│   │   └── pipeline.py     # High-level orchestration (collect → download)
│   └── storage/
│       ├── file_manager.py # CBZ archive creation and management
│       └── url_builder.py  # URL construction with episode-offset logic
│
├── data/
│   ├── data.py             # Excel reader that feeds the library
│   └── data.xlsx           # Your comic registry (not committed)
│
├── sources/
│   ├── __init__.py         # Dynamic module loader
│   ├── Asura.py
│   ├── Rizz.py
│   └── Webtoon.py
│
├── tests/
└── utils/
    ├── scraper.py          # HTTP helpers (fetch HTML, fetch image bytes)
    └── utils.py            # Thread pool, title sanitiser, reorder logic
```

---

## How It Works

```plaintext
main.py
  └─ loads all source plugins          (sources/__init__.py)
  └─ sets up logging                   (core/logging/logger.py)
  └─ builds a Library                  (core/services/library.py  ←  data/data.py)
  └─ runs the Pipeline                 (core/services/pipeline.py)
        ├─ COLLECT phase (spinner)
        │    for each comic in the library:
        │      Scraper.get_available_episodes()      →  set of ints on the site
        │      FileManager.get_downloaded_episodes() →  set of ints on disk
        │      missing = available − downloaded
        │
        └─ DOWNLOAD phase (progress bar)
             for each missing episode:
               Scraper.get_url_images_episode(ep)   →  list of image URLs
               ThreadPool downloads all images in parallel
               Image bytes → (optional WEBP conversion) → written into .cbz
```

Every source class registers itself automatically via `Scraper.__init_subclass__`, so importing the `sources/` directory is enough to make all scrapers available.

---

## Requirements

- Python 3.12 or newer
- [uv](https://github.com/astral-sh/uv) package manager
- Chromium browser via Playwright (only needed for JS-heavy sources)

---

## Installation

```bash
git clone <your-repo-url>
cd comic-downloader

uv sync
uv run playwright install chromium
```

---

## Configuration

Create these two files in the project root (both are gitignored):

### `.env.path` — download folder

```env
BASE_PATH=/home/yourname/Comics
```

Defaults to `~/Comics` if absent.

### `.env.cookies` — optional session cookies

```env
WEBTOON=your_session_cookie_here
TAPAS=
VORTEX=
FLAME=
```

The key name must match the source class name in **lowercase** (e.g., the `Webtoon` class reads `WEBTOON`). Leave variables empty if you don't need authentication for that source.

---

## Managing your comic list

### data/data.xlsx structure

| Column | Description |
| --- | --- |
| `source` | Scraper to use. Must match a source class name (lowercase). |
| `completed` | Truthy value skips the comic entirely. |
| `<source>_title` | Human-readable title. |
| `<source>_id` | Site-specific identifier (see below). |

Because a comic might exist on multiple platforms, columns are source-prefixed. For a row where `source = webtoon`, the script reads `webtoon_title` and `webtoon_id`.

### Adding a comic

1. Open `data/data.xlsx` and add a new row.
2. Set `source` to the scraper name (e.g. `webtoon`, `asura`, `rizz`).
3. Fill in `<source>_title` and `<source>_id`.
4. Set `completed` to `FALSE`.

**Finding the ID:**

- **Webtoon:** the `title_no` query parameter — for `.../list?title_no=95` the ID is `95`.
- **Asura:** the slug before the hash — for `.../comics/solo-leveling-26f76d6d` the ID is `solo-leveling`.
- **Rizz:** the slug after `r2311170-` — for `.../series/r2311170-my-comic` the ID is `my-comic`.

---

## Running the downloader

```bash
uv run main.py
```

To customise which comics are processed, edit `get_library()` in `main.py`:

```python
def get_library() -> Library:
    completed = False
    sources = ("asura", "webtoon")
    return Library().shuffle().filter_by(completed=completed, source=sources).reorder("source")
```

Available `Library` methods:

| Method | Description |
| --- | --- |
| `.filter_by(**kwargs)` | Keep only rows matching all keyword arguments. |
| `.sort_by(*keys)` | Sort alphabetically by one or more column names. |
| `.shuffle()` | Randomise order. |
| `.reorder(*keys)` | Interleave by key so sources alternate. |
| `.show()` | Print the current library as a Rich table. |

---

## Output format

```plaintext
<BASE_PATH>/<Sanitized Comic Title>/0001.cbz
<BASE_PATH>/<Sanitized Comic Title>/0002.cbz
...
```

The title is sanitised so it is safe on all file systems: characters like `:`, `?`, `*`, `/`, and `\` are replaced with visually similar Unicode equivalents. A `.cbz` file is a standard ZIP archive containing numbered image files (`001.webp`, `002.jpg`, etc.) that any comic reader can open directly.

---

## Supported sources

| Class | Site | JS needed | Converts to WEBP |
| --- | --- | --- | --- |
| `Webtoon` | webtoons.com | No | Yes |
| `Asura` | asurascans.com | No | No |
| `Rizz` | rizzfables.com | No | No |

---

## Adding a new source

Create `sources/MySource.py`. The class is registered automatically — no changes to any other file are needed.

### Required class attributes

```python
from core import Scraper

class MySource(Scraper):

    # URL patterns. Use {comic_id} and {episode} as placeholders.
    PATTERNS: dict[str, str] = {
        "series":  "https://mysite.com/series/{comic_id}",
        "episode": "https://mysite.com/series/{comic_id}/ch/{episode}",
    }

    # CSS selector and attribute for the episode images on the episode page.
    IMAGES_CSS: tuple[str, str] = ("#reader img", "src")

    # CSS selector and attribute that exposes the last available episode number.
    # The scraped text must be castable to int.
    LAST_EPISODE_CSS: tuple[str, str] = (".chapters a:first-child", "data-chapter")

    # Referer header sent with every image request.
    REFERER: str = "https://mysite.com/"

    # True → convert images to WEBP. False → keep original format.
    COMPRESSION: bool = False
```

### Optional overrides

Override `_get_available_episodes` if the site does not expose a simple last-episode number:

```python
def _get_available_episodes(self) -> set[int]:
    html = self.get_comic_html()
    nodes = html.css(".episode-item")
    return {int(node.attributes["data-num"]) for node in nodes}
```

Override `_get_url_images_episode` if images require JSON parsing or a different fetch strategy:

```python
def _get_url_images_episode(self, episode: int) -> list[str]:
    from utils.scraper import get_html_parsed
    html = get_html_parsed(self.url_episode(episode))
    # extract and return list of absolute image URL strings
    return [...]
```

Both methods have logging and exception-handling wrappers in the base class.

Finally, add a row to `data/data.xlsx` with `source = mysource` and the corresponding `mysource_title` / `mysource_id` columns.

---

## Episode numbering and skips

Some series have chapters removed from the official site. The `URLBuilder.skip` dictionary handles this transparently:

```python
# core/storage/url_builder.py
skip: dict[str, set[int]] = {
    "Tower of God": {221},
}
```

When local episode 221 is requested, the URL is built for server episode 222. The offset accumulates: if episodes 50 and 100 are both skipped, local episode 150 fetches URL 152. To add a skip for your comic:

```python
skip: dict[str, set[int]] = {
    "Tower of God": {221},
    "My Comic":     {15, 16},
}
```

---

## Troubleshooting

**`ModuleNotFoundError`** — run `uv sync`.

**Playwright / browser errors** — run `uv run playwright install chromium`. On headless servers you may also need `playwright install-deps chromium`.

**`Source for "..." not found`** — the `source` column in your spreadsheet does not match any class name in `sources/`. Check for typos; names are matched in lowercase.

**`Failed to fetch data` or HTTP errors** — the site may have changed its HTML structure (update the CSS selectors), or you may need a session cookie in `.env.cookies`.

**CSS selector matches nothing** — a `logs/debug.html` file is written automatically with the page content at the time of failure. Inspect it to find the correct selector.

**`More downloaded episodes than available`** — chapters were removed from the site after you downloaded them. The downloader logs a warning and continues; no action is required.
