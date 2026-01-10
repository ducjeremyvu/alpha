# base modules
from edge_tools.logger import setup_logging
from edge_tools.db.migrations import load_all_tables


import logging

logger = logging.getLogger(__name__)


def main():
    setup_logging(logging.DEBUG)

    load_all_tables()


if __name__ == "__main__":
    main()
