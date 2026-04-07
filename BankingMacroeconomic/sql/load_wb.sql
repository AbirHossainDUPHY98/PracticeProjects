CREATE TEMP TABLE temp_wb (
    year INT,
    value NUMERIC,
    indicator TEXT
);

\copy temp_wb FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/world_bank1_clean.csv' CSV HEADER;
\copy temp_wb FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/world_bank2_clean.csv' CSV HEADER;

INSERT INTO dim_time(year)
SELECT DISTINCT year
FROM temp_wb
ON CONFLICT DO NOTHING;

INSERT INTO dim_source(source_name)
VALUES ('world_bank')
ON CONFLICT DO NOTHING;

INSERT INTO dim_indicator(indicator_code, indicator_name, domain)
SELECT DISTINCT indicator, indicator,
       CASE WHEN indicator LIKE '%Loan%' OR indicator LIKE '%Deposit%' THEN 'banking'
            ELSE 'macro' END
FROM temp_wb
ON CONFLICT DO NOTHING;

INSERT INTO fact_macro(time_id, indicator_id, value, source_id)
SELECT t.time_id, i.indicator_id, w.value, s.source_id
FROM temp_wb w
JOIN dim_time t ON w.year = t.year
JOIN dim_indicator i ON w.indicator = i.indicator_code
JOIN dim_source s ON s.source_name = 'world_bank'
WHERE i.domain = 'macro';

INSERT INTO fact_banking(time_id, indicator_id, value, source_id)
SELECT t.time_id, i.indicator_id, w.value, s.source_id
FROM temp_wb w
JOIN dim_time t ON w.year = t.year
JOIN dim_indicator i ON w.indicator = i.indicator_code
JOIN dim_source s ON s.source_id = s.source_id
WHERE i.domain = 'banking';

DROP TABLE temp_wb;

