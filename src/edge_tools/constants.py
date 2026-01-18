from dotenv import load_dotenv
import os

load_dotenv()

DATAPATH = os.getenv("DATAPATH", "price_data")
