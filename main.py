import edge_tools as et

from src.edge_tools.logger import setup_logging
from src.edge_tools.database import insert_minute_file_data
import logging

from datetime import datetime

selected_date = datetime(2025, 11, 5)



def main():
    setup_logging(logging.INFO) 

    insert_minute_file_data()



    
if __name__=='__main__':
    main()
