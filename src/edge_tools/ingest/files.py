from ..constants import DATAPATH

import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def assign_data_path(datapath: str = None) -> Path:
    """Assigns the data path for price data storage.

    Args: datapath (str, optional): Custom data path. Defaults to None.

    Returns: Path: The assigned data path as a Path object.
    """
    if not datapath:
        datapath = DATAPATH
    logger.debug(f"Data path assigned to: {datapath}")
    return Path(datapath).expanduser()


def get_unwritten_files(folder: Path, interval: str = "Minute") -> list[Path]:
    """Retrieves a list of files in the specified folder that have not been marked as done.
    Args:
        folder (Path): The folder to search for files.
        symbol (str, optional): The symbol to filter files. Defaults to "US500".
        interval (str, optional): The interval to filter files. Defaults to "Minute".
    Returns:
        list[Path]: A list of Path objects representing the unwritten files.
    """
    files = [
        f
        for f in folder.iterdir()
        if f.is_file()
        and f"_{interval}_" in f.name
        and "_done" not in f.name
        and f.name.endswith(".csv")
    ]
    logger.debug(f"Unwritten files found: {[str(f) for f in files]}")
    return files


def extract_symbol_from_filename(filename: Path) -> str:
    """Extracts the symbol from a given filename.
    Args:
        filename (str): The filename to extract the symbol from.
    Returns:
        str: The extracted symbol.
    """
    symbol = filename.name.split("_")[0]
    return symbol


# Dict comprehension: map symbol (from filename) to Path object
def map_symbols_to_files(files: list[Path]) -> dict[str, Path]:
    """
    Creates a dictionary mapping symbols (extracted from filenames) to their Path objects.
    Args:
        files (list[Path]): List of file paths.
    Returns:
        dict[str, Path]: Dictionary mapping symbol to Path.
    """
    return {extract_symbol_from_filename(f): f for f in files}


def get_absolute_filepath(path: Path) -> str:
    """Convert a Path object to its absolute filepath string.

    Args:
        path (Path): The Path object to convert

    Returns:
        str: The absolute filepath as a string
    """
    return str(path.absolute())


def build_symbol_file_records(symbol_file_map: dict[str, Path]) -> list[dict]:
    """Convert a mapping of symbol -> Path into a list of dicts:
    [{ "path": Path object, "parameter": {"symbol": symbol, "file_path_csv": path_str} }, ...]
    """
    records: list[dict] = []
    for symbol, path_obj in symbol_file_map.items():
        path_str = (
            get_absolute_filepath(path_obj)
            if isinstance(path_obj, Path)
            else str(path_obj)
        )
        file_start, file_end = _detect_time_range(path_obj)
        records.append(
            {
                "path": path_obj,
                "parameter": {
                    "symbol": symbol,
                    "file_path_csv": path_str,
                    "file_start": file_start,
                    "file_end": file_end,
                },
            }
        )
    logger.debug(f"Built symbol file records: {records}")
    return records


def _detect_time_range(path_obj: Path) -> tuple[str | None, str | None]:
    if not isinstance(path_obj, Path) or not path_obj.exists():
        return None, None
    try:
        with path_obj.open("r", encoding="utf-8") as handle:
            header = handle.readline()
            if not header:
                return None, None
            time_index = _find_time_index(header)
            first_row = handle.readline()
            if not first_row:
                return None, None
            first_time = _parse_time_from_row(first_row, time_index)
            last_time = None
            for line in handle:
                last_time = _parse_time_from_row(line, time_index)
            if last_time is None:
                last_time = first_time
            return first_time, last_time
    except OSError:
        return None, None


def _find_time_index(header: str) -> int:
    columns = [col.strip().strip("\ufeff") for col in header.split(",")]
    for idx, name in enumerate(columns):
        if name.lower() == "time":
            return idx
    return 0


def _parse_time_from_row(row: str, time_index: int) -> str | None:
    values = [val.strip() for val in row.split(",")]
    if time_index >= len(values):
        return None
    return values[time_index] or None


def mark_file_as_done(file_path: Path) -> Path:
    """Renames a file by appending '_done' before the extension.

    Args:
        file_path (Path): Path object of the file to rename

    Returns:
        Path: Path object of the renamed file
    """
    new_name = file_path.stem + "_done" + file_path.suffix
    new_path = file_path.parent / new_name
    file_path.rename(new_path)
    logger.debug(f"File renamed from {file_path} to {new_path}")
    return new_path
