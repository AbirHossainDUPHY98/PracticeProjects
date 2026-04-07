-- Load macro CSV into temporary table
CREATE TEMP TABLE temp_macro (
    year INT,
    indicator TEXT,
    value NUMERIC
);

\copy temp_macro FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/bd_macro_indicators_clean.csv' CSV HEADER;

INSERT INTO dim_time(year)
SELECT DISTINCT year
FROM temp_macro
ON CONFLICT DO NOTHING;

INSERT INTO dim_source(source_name)
VALUES ('bd_macro')
ON CONFLICT DO NOTHING;

INSERT INTO dim_indicator(indicator_code, indicator_name, domain)
SELECT DISTINCT indicator, indicator, 'macro'
FROM temp_macro
ON CONFLICT DO NOTHING;

INSERT INTO fact_macro(time_id, indicator_id, value, source_id)
SELECT
    t.time_id,
    i.indicator_id,
    m.value,
    s.source_id
FROM temp_macro m
JOIN dim_time t ON m.year = t.year
JOIN dim_indicator i ON m.indicator = i.indicator_code
JOIN dim_source s ON s.source_name = 'bd_macro';

DROP TABLE temp_macro;

