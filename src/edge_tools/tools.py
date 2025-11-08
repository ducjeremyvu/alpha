from pathlib import Path

from .database import get_duckdb_connection



DATAPATH = "/Users/ducjeremyvu/trading/price_data"

with get_duckdb_connection() as con:
    # perform database operations
    pass  # replace with actual operations


def assign_data_path(datapath: str = None) -> Path:
    if not datapath:
        datapath = DATAPATH
    return Path(datapath)


def get_unwritten_files(folder: Path, symbol: str = "US500", interval: str = "Minute") -> list[Path]:
    files = [
        f for f in folder.iterdir()
        if f.is_file()
        and f.name.startswith(f"{symbol}_{interval}_")
        and "_done" not in f.name
    ]
    return files


if __name__ == "__main__": 
    print("Edge tools module")
    with get_duckdb_connection() as con:
        print("Database connection established.")

    normal_path = assign_data_path()
    print(f"Data path assigned to: {normal_path}")
    other_path = assign_data_path("/custom/data/path")
    print(f"Custom data path assigned to: {other_path}")

    folder = normal_path
    files = [
        f for f in folder.iterdir()
        if f.is_file()
        and f.name.startswith("US500_Minute_")
        and "_done" not in f.name
    ]
    print(files)