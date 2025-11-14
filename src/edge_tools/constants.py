from dotenv import load_dotenv
import os 

load_dotenv()

DATAPATH = os.getenv("DATAPATH", "/Users/ducjeremyvu/trading/price_data")

# alternative below makes it OS independent
# DATAPATH = Path(os.getenv("DATAPATH", "/Users/ducjeremyvu/trading/price_data")).expanduser()