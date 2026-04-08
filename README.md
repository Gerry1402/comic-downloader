# Comic Downloader

A Python script that downloads comic/manhwa chapters from supported sites and saves each episode as a `.cbz` file.

## What this project does

- Loads a list of comics from `data/data.xlsx`.
- Detects each comic source (for example `webtoon`, `asura`, `rizz`).
- Checks which episodes are already downloaded.
- Downloads only missing episodes.
- Saves every episode as a `.cbz` archive in your comics folder.
- Stores last download timestamps in `data/dates.json`.

## Supported sources

Current source classes in this repo:

- `Webtoon`
- `Asura`
- `Rizz`

## How it works (simple flow)

1. `main.py` loads all source modules.
2. It builds a comic list from `Comic.data` (loaded from `data/data.xlsx`).
3. For each comic not marked as completed, it finds missing episodes.
4. It downloads episode images in parallel (thread pool).
5. It packages images into `0001.cbz`, `0002.cbz`, etc.
6. It updates logs/timestamps.

## Requirements

- Python 3.11+ recommended
- Chromium browser for Playwright (used by Asura pages)

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

This project reads settings from two env files:

- `.env.path`
- `.env.cookies`

### 1) Set download folder

In `.env.path`:

```env
BASE_PATH=X:/Comics/Ongoing
```

Use any path you want, for example `C:/Users/<you>/Comics`.

### 2) Optional cookies (if a source needs auth/session)

In `.env.cookies` you can add values like:

```env
WEBTOON=
TAPAS=
VORTEX=
FLAME=
```

If you do not need cookies for your sources, this file can stay empty.

## Run the downloader

```bash
python main.py
```

By default, it loops over all available comics and downloads missing episodes.

## Download only one comic (example)

Use a small one-liner from terminal:

```bash
python -c "from sources import load_all_modules; from sources.Comic import Comic; load_all_modules(); Comic.create('Jungle Juice').download_all()"
```

You can replace `Jungle Juice` with any title present in your data file.

## Where files are saved

Output folder format:

```text
<BASE_PATH>/<Sanitized Comic Title>/0001.cbz
<BASE_PATH>/<Sanitized Comic Title>/0002.cbz
...
```

Episode numbers are zero-padded to 4 digits.

## Data files

- `data/data.xlsx`: main comic registry (titles, ids, source, completed flag)
- `data/dates.json`: last successful download timestamps
- `done.json`: simple log of processed episodes
- `error.json`: created automatically when image downloads fail

## Add or edit comics

Edit `data/data.xlsx` and keep the same structure already used by the script:

- A title and ID for each source type
- A `source` column with values that match the loader keys (for example `webtoon`, `asura`, `rizz`)
- A `completed` column (truthy values are skipped by `main.py`)

After editing, run again:

```bash
python main.py
```

## Troubleshooting

- `ModuleNotFoundError`: install dependencies from `requirements.txt`.
- Playwright/browser errors: run `playwright install chromium`.
- `Source for "..." not found`: source value in your data does not match a loaded source class.
- `Failed to fetch data` or image errors: site layout changed, URL blocked, or cookies needed.

## Notes

- Downloading content should respect each site's Terms of Service and copyright rules.
- This repository is intended for personal use/backup workflows.
