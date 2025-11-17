import duckdb
from .base import MetricDefinition
import logging

logger = logging.getLogger(__name__)


# List every metric module here
ALL_METRICS = [
    # thirty_min_open_change,
    # add more metrics here
]

def ensure_metric_registered(conn, metric: MetricDefinition):
    meta = metric
    logger.debug(meta)
    # Insert or ignore
    conn.execute(
        """
            INSERT OR IGNORE INTO metrics (metric_name, description, dataset, time_window, unit, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, 
        [
            meta.name, 
            meta.description,
            meta.dataset, 
            meta.window, 
            meta.unit, 
            meta.category
            ]
    )

    # Fetch metric_id
    metric_id = conn.execute("""
        SELECT metric_id FROM metrics WHERE metric_name = ?
    """, [meta.name]).fetchone()[0]

    return metric_id