CREATE TEMP TABLE temp_fsi (
    indicator TEXT,
    year INT,
    value NUMERIC
);

\copy temp_fsi FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/fsi_loans_total_clean.csv' CSV HEADER;
\copy temp_fsi FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/fsi_loans_domestic_clean.csv' CSV HEADER;
\copy temp_fsi FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/fsi_deposits_to_loans_clean.csv' CSV HEADER;
\copy temp_fsi FROM '/home/abir/PaPa/MyGym/DataPractice/BankingMacroeconomicAnalysisBD/data_clean/fsi_nonperforming_loans_clean.csv' CSV HEADER;

INSERT INTO dim_time(year)
SELECT DISTINCT year
FROM temp_fsi
ON CONFLICT DO NOTHING;

INSERT INTO dim_source(source_name)
VALUES ('fsi')
ON CONFLICT DO NOTHING;

INSERT INTO dim_indicator(indicator_code, indicator_name, domain)
SELECT DISTINCT indicator, indicator, 'banking'
FROM temp_fsi
ON CONFLICT DO NOTHING;

INSERT INTO fact_banking(time_id, indicator_id, value, source_id)
SELECT
    t.time_id,
    i.indicator_id,
    f.value,
    s.source_id
FROM temp_fsi f
JOIN dim_time t ON f.year = t.year
JOIN dim_indicator i ON f.indicator = i.indicator_code
JOIN dim_source s ON s.source_name = 'fsi';

DROP TABLE temp_fsi;

