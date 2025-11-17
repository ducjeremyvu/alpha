# base modules 
from edge_tools.logger import setup_logging
from edge_tools.db.migrations import create_tables_from_query
from edge_tools.db import delete_table, get_duckdb_connection

import logging

logger = logging.getLogger(__name__)

def recreate_metrics_tables() -> None:
    """ deletes and recreates metrics tables 

    order is important, which is why it deletes objects in the following order:
    1. metric_events
    2. metrics
    3. id_sequence_metrics
    
    return:
        nothing
    """

    con = get_duckdb_connection()
    # use below, if accidentally deleted id_sequence_metrics beforhand
    # con.execute("CREATE SEQUENCE IF NOT EXISTS id_sequence_metrics START 1;")

    delete_table('metric_events', con)
    delete_table('metrics', con)
    con.execute("""DROP SEQUENCE IF EXISTS id_sequence_metrics;""")
    logger.info("Deleted sequence id_sequence")
    con.close()

    create_tables_from_query("create_table_metrics")


def main():
    setup_logging(logging.DEBUG) 

    recreate_metrics_tables()

if __name__=='__main__':
    main()
