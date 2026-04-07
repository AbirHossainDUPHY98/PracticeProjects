CREATE OR REPLACE VIEW macro_prepared AS
SELECT
    i.indicator_name AS indicator_name,
    t.year,
    f.value,
    CASE
        WHEN LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year) IS NULL
        THEN NULL
        ELSE (f.value - LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year))
             * 100.0
             / NULLIF(LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year), 0)
    END AS change_per_year
FROM dim_time t
LEFT JOIN fact_macro f ON f.time_id = t.time_id
LEFT JOIN dim_indicator i ON f.indicator_id = i.indicator_id
ORDER BY i.indicator_name, t.year;

CREATE OR REPLACE VIEW banking_prepared AS
SELECT
    i.indicator_name AS indicator_name,
    t.year,
    f.value,
    CASE
        WHEN LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year) IS NULL
        THEN NULL
        ELSE (f.value - LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year))
             * 100.0
             / NULLIF(LAG(f.value) OVER (PARTITION BY f.indicator_id ORDER BY t.year), 0)
    END AS change_per_year
FROM dim_time t
LEFT JOIN fact_banking f ON f.time_id = t.time_id
LEFT JOIN dim_indicator i ON f.indicator_id = i.indicator_id
ORDER BY i.indicator_name, t.year;

CREATE OR REPLACE VIEW macro_banking_overlap AS
SELECT *
FROM macro_prepared
WHERE year >= 2011
UNION ALL
SELECT *
FROM banking_prepared
WHERE year >= 2011
ORDER BY indicator_name, year;
