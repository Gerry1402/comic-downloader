import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.comic import Comic


class Logger:
    dir_path: Path = Path(__file__).parent.parent / "logs"
    log_results: tuple[str, str] = ("error", "done")
    ignore_successful_logs: bool = True

    def __init__(self, name: str, comic: Comic) -> None:
        self.name = name
        self.comic = comic

    def get_file_path(self, log_type: str, successfull: bool) -> Path:
        name = ".".join([self.name, log_type, self.log_results[int(successfull)]])
        file_path = self.dir_path / f"{name}.jsonl"
        self.dir_path.mkdir(exist_ok=True)
        # file_path.touch(exist_ok=True)
        return file_path

    def add(self, log_type: str, is_fail: bool, **kwargs: Any) -> None:  # noqa: ANN401
        if self.ignore_successful_logs and not is_fail:
            return
        file_path = self.get_file_path(log_type, is_fail)
        data = {"time": datetime.now().isoformat(), "comic": self.comic.title, **kwargs}
        with file_path.open("a", encoding="utf-8") as f:
            f.write(f"{json.dumps(data)}\n")

    @staticmethod
    def sort_jsonl(file_path: Path, keys: list[str]) -> None:
        with file_path.open("r", encoding="utf-8") as f:
            data = [json.loads(line.strip()) for line in f if line.strip()]
        data.sort(key=lambda x: (x[key] for key in keys))
        with file_path.open("w", encoding="utf-8") as f:
            for item in data:
                f.write(f"{json.dumps(item)}\n")
