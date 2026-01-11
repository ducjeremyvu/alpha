from .time import preprocess_for_premarket_analysis
from .ohlcv import ohlcv_for_date_and_prev, normalize_ohlcv
from datetime import time
import pandas as pd

import logging

logger = logging.getLogger(__name__)


class PremarketPriceCalculator:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self._trading_dates = sorted(set(self.data.index.date))
        self._valid = True
        logger.debug(f"Trading dates in data: {self._trading_dates}")
        if len(self._trading_dates) < 2:
            self._valid = False
            raise ValueError("Not enough data to compute previous day's close.")
        if len(self._trading_dates) > 2:
            self._valid = False
            raise ValueError(
                "Data contains more than two trading dates. Please provide data for only the selected date and previous date."
            )
        self._selections = {
            "us_close_previous_day": {
                "date_select": 0,
                "column_name": "ny_time",
                "time": time(16),
            },
            "tokyo_open": {
                "date_select": -1,
                "column_name": "tokyo_time",
                "time": time(9),
            },
            "london_open": {
                "date_select": -1,
                "column_name": "london_time",
                "time": time(9),
            },
            "t_minus_60": {
                "date_select": -1,
                "column_name": "ny_time",
                "time": time(8, 30),
            },
            "t_minus_30": {
                "date_select": -1,
                "column_name": "ny_time",
                "time": time(9, 0),
            },
            "t_minus_15": {
                "date_select": -1,
                "column_name": "ny_time",
                "time": time(9, 15),
            },
            "us_open_current_day": {
                "date_select": -1,
                "column_name": "ny_time",
                "time": time(9, 30),
            },
            "us_close_current_day": {
                "date_select": -1,
                "column_name": "ny_time",
                "time": time(16),
            },
        }

    def compute_price(self, selection_key: str) -> float:
        """
        Computes price based on selection parameters.

        Parameters:
        selection_key (str): Key to select price computation parameters ('us_close', 'tokyo_open', 'london_open')

        Returns:
        float: Computed price value
        """
        logger.debug(f"Computing price for selection key: {selection_key}")
        # Get parameters for the selected price type
        params = self._selections.get(selection_key)
        if not params:
            raise ValueError(f"Invalid selection key: {selection_key}")
        logger.debug(f"Selection parameters: {params}")

        target_date = params["date_select"]
        column_name = params["column_name"]
        target_time = params["time"]

        prev_date = self._trading_dates[target_date]
        logger.debug(f"Target date for computation: {prev_date}")
        # Filter data for the previous trading date
        prev_day_data = self.data[self.data[column_name].dt.date == prev_date]
        logger.debug(f"Previous day data:\n{prev_day_data['ny_time']}")
        if prev_day_data.empty:
            raise ValueError("No data found for the previous trading date.")

        # Get the last closing price of the previous trading day
        try:
            price = prev_day_data.loc[
                prev_day_data[f"{column_name}_only"] == target_time
            ].iloc[0]["close"]
            logger.debug(f"Computed price for {selection_key}: {price}")
        except IndexError:
            raise ValueError(
                f"No data found for the specified time {target_time} on {prev_date}."
            )
        return price


def compute_premarket_prices(sliced_data):

    premarket_calculator = PremarketPriceCalculator(sliced_data)

    if premarket_calculator._valid is False:
        return {
            "us_close_previous_day": None,
            "tokyo_open": None,
            "london_open": None,
            "t_minus_60": None,
            "t_minus_30": None,
            "t_minus_15": None,
            "us_open_current_day": None,
            "us_close_current_day": None,
        }

    us_close_previous_day_price = premarket_calculator.compute_price(
        "us_close_previous_day"
    )
    tokyo_open_price = premarket_calculator.compute_price("tokyo_open")
    london_open_price = premarket_calculator.compute_price("london_open")
    t_minus_60_price = premarket_calculator.compute_price("t_minus_60")
    t_minus_30_price = premarket_calculator.compute_price("t_minus_30")
    t_minus_15_price = premarket_calculator.compute_price("t_minus_15")
    us_open_current_day_price = premarket_calculator.compute_price(
        "us_open_current_day"
    )
    us_close_current_day_price = premarket_calculator.compute_price(
        "us_close_current_day"
    )

    logger.debug(
        f"Premarket Prices Computed: {{'us_close_previous_day': {us_close_previous_day_price}, 'tokyo_open': {tokyo_open_price}, 'london_open': {london_open_price}, 't_minus_60': {t_minus_60_price}, 't_minus_30': {t_minus_30_price}, 't_minus_15': {t_minus_15_price}, 'us_open_current_day': {us_open_current_day_price}, 'us_close_current_day': {us_close_current_day_price}}}"
    )

    return {
        "us_close_previous_day": us_close_previous_day_price,
        "tokyo_open": tokyo_open_price,
        "london_open": london_open_price,
        "t_minus_60": t_minus_60_price,
        "t_minus_30": t_minus_30_price,
        "t_minus_15": t_minus_15_price,
        "us_open_current_day": us_open_current_day_price,
        "us_close_current_day": us_close_current_day_price,
    }


def compute_changes(premarket_prices):
    """
    Computes percentage changes for pre-market prices.
    Parameters:
    premarket_prices (dict): Dictionary containing pre-market prices.
    Returns:
    dict: A dictionary containing computed percentage changes.
    """

    def pct(a, b):
        if b is None or b == 0 or a is None:
            return None
        return round(((a - b) / b) * 100, 2)

    prev_close = premarket_prices.get("us_close_previous_day")
    tokyo_open = premarket_prices.get("tokyo_open")
    london_open = premarket_prices.get("london_open")
    t_minus_60_price = premarket_prices.get("t_minus_60")
    t_minus_30_price = premarket_prices.get("t_minus_30")
    t_minus_15_price = premarket_prices.get("t_minus_15")
    us_open_price = premarket_prices.get("us_open_current_day")
    us_close_price = premarket_prices.get("us_close_current_day")

    return {
        "tokyo_change_percent": pct(tokyo_open, prev_close),
        "london_change_percent": pct(london_open, prev_close),
        "t_minus_60_change_percent": pct(t_minus_60_price, prev_close),
        "t_minus_30_change_percent": pct(t_minus_30_price, prev_close),
        "t_minus_15_change_percent": pct(t_minus_15_price, prev_close),
        "prev_close_to_us_open_change_percent": pct(us_open_price, prev_close),
        "prev_close_to_us_close_change_percent": pct(us_close_price, prev_close),
        "us_open_to_us_close_change_percent_current_day": pct(
            us_close_price, us_open_price
        ),
    }


def premarket_data(symbol, selected_date):
    data = ohlcv_for_date_and_prev(symbol=symbol, selected_date=selected_date)
    data = normalize_ohlcv(data, style="lowercase")
    data = preprocess_for_premarket_analysis(data)
    return data


def compute_premarket_prices_and_changes(data):
    premarket_prices = compute_premarket_prices(data)
    changes = compute_changes(premarket_prices)
    return {**premarket_prices, **changes}


def compute_metrics(symbol="US500", selected_date=None):
    """
    Computes pre-market prices and changes for a given symbol and selected date.
    Parameters:
    symbol (str): The trading symbol (default is "US500").
    selected_date (datetime.date): The selected date for analysis.
    Returns:    tuple: A tuple containing the metrics dictionary and the premarket data DataFrame.
    """
    # Slice data for the selected date and previous date
    data = premarket_data(symbol, selected_date)
    logger.debug(f"Data for {symbol} on {selected_date}:\n{data}")
    premarket_prices = compute_premarket_prices(data)
    changes = compute_changes(premarket_prices)

    return {**premarket_prices, **changes}, data


def filter_us_market_hours(data: pd.DataFrame, end_time: str = "16:00") -> pd.DataFrame:
    """
    Filters the DataFrame to include only rows where the US market is open (09:30 to 16:00 NY time).

    Parameters:
    data (pd.DataFrame): DataFrame with a 'ny_time_only' column containing time objects.

    Returns:
    pd.DataFrame: Filtered DataFrame with only US market hours.
    """
    # Define US open/close bounds
    open_time = pd.to_datetime("09:30").time()
    close_time = pd.to_datetime(end_time).time()

    # Filter only market hours
    filtered_data = data[data["ny_time_only"].between(open_time, close_time)]

    return filtered_data


def filter_last_day(data: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the DataFrame to include only rows from the last trading day in the data.

    Parameters:
    data (pd.DataFrame): DataFrame with a 'date_only' column containing date objects.

    Returns:
    pd.DataFrame: Filtered DataFrame with only the last trading day.
    """
    if data.empty:
        return data

    last_date = data["ny_time"].dt.date.max()
    logger.debug(f"Last trading date in data: {last_date}")
    filtered_data = data[data["ny_time"].dt.date == last_date]

    return filtered_data


def filter_today_first_30_minutes(data: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the DataFrame to include only rows from the first 30 minutes of today's US market hours (09:30 to 10:00 NY time).

    Parameters:
    data (pd.DataFrame): DataFrame with a 'ny_time_only' column containing time objects.

    Returns:
    pd.DataFrame: Filtered DataFrame with only the first 30 minutes of today's US market hours.
    """
    filtered_data = filter_us_market_hours(data, end_time="10:00")
    logger.debug(f"Data after filtering US market hours:\n{filtered_data}")
    filtered_data = filter_last_day(filtered_data)
    logger.debug(f"Data after filtering today's date:\n{filtered_data}")

    return filtered_data
