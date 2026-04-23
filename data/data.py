from pathlib import Path

import pandas as pd

data_path = Path(__file__).parent / "data.xlsx"


def get_data_as_dict() -> dict:
    df = pd.read_excel(data_path.with_suffix(".xlsx"), header=None)
    sources = {name.split()[0]: i for i, name in enumerate(df.iloc[0].tolist()[:-1])}
    data = {}

    for _, row in df.iloc[1:].iterrows():
        source: str = row.iloc[-2]
        is_completed: str = row.iloc[-1]
        index = sources[source]
        data[row.iloc[index - 1]] = (row.iloc[index], source, is_completed)

    return data


if __name__ == "__main__":
    print(get_data_as_dict())
    # print(read_secondary_sheet())
