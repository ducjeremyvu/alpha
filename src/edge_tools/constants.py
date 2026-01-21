from dotenv import load_dotenv
import os

load_dotenv()

DATAPATH = os.getenv("DATAPATH", "price_data")
TIMEFRAME_SOURCE = os.getenv("TIMEFRAME_SOURCE", "auto")
RESAMPLE_TIMEFRAMES = os.getenv(
    "RESAMPLE_TIMEFRAMES", "15m,30m,1h,1d,1w,1d_rth"
)
