SELECT
    date_trunc('hour', CAST('{{start_time}}' AS TIMESTAMPTZ)) AS aligned_start,
    date_trunc('hour', CAST('{{end_time}}' AS TIMESTAMPTZ) + INTERVAL '1 hour') AS aligned_end;
