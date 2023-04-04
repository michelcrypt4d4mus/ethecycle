-- For sqlite3
.headers on
.mode csv

.output wallets_table_dump.csv
SELECT * FROM wallets;

.output tokens_table_dump.csv
SELECT * FROM tokens;

.output data_sources.csv
SELECT * FROM data_sources;
