from pathlib import Path

import pandas as pd
from pandas import Series

data_path: Path = Path(__file__).parent / "data.xlsx"


def str_to_int(s: str) -> int | str:
    try:
        number = float(s)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return s


def data_row(row: Series) -> dict[str, str | bool]:
    source = row["source"]

    return {
        "title": row[f"{source}_title"],
        "id": str_to_int(row[f"{source}_id"]),
        "source": source,
        "completed": row["completed"],
    }


class Data:
    data_df: pd.DataFrame | None = None

    @classmethod
    def get_df(cls) -> pd.DataFrame:
        if cls.data_df is None:
            cls.data_df = pd.read_excel(data_path, header=0)
        return cls.data_df

    @classmethod
    def get_data(cls) -> list[dict[str, str | bool]]:
        return cls.get_df().apply(data_row, axis=1).tolist()

    @classmethod
    def get_sources(cls) -> tuple[str]:
        return tuple(sorted(set(cls.get_df()["source"].unique())))
