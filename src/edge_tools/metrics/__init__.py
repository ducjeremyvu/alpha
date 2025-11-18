import logging 

logger = logging.getLogger(__name__)


def pivot_metrics(con):

    merged_cte = """
        WITH merged AS (
            SELECT 
                me.date,
                me.symbol,
                m.metric_name,
                me.metric_value AS value
            FROM metric_events me
            LEFT JOIN metrics m USING (metric_id)
        )
    """

    # Create the column list with manually quoted identifiers
    cols = con.execute(f"""
        {merged_cte}
        SELECT string_agg('"' || metric_name || '"', ', ')
        FROM (SELECT DISTINCT metric_name FROM merged)
    """).fetchone()[0]

    sql = f"""de 
        {merged_cte}
        SELECT *
        FROM merged
        PIVOT (
            ANY_VALUE(value)
            FOR metric_name IN ({cols})
        )
        ORDER BY date, symbol;
    """
    logger.debug(sql)
    return con.execute(sql).df()


