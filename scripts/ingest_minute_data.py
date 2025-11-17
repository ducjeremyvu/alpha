# importing testing modules from
from edge_tools.utils import setup_logging
from edge_tools.ingest import insert_minute_file_data, insert_file_data

import logging



logger = logging.getLogger(__name__)


def main():
    setup_logging(logging.DEBUG) 
    # insert_minute_file_data()
    insert_file_data()
    
if __name__=='__main__':
    main()
