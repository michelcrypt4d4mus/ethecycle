-- For sqlite3
.headers on
.mode csv

.output wallet_tags.csv
SELECT * FROM wallets;

.output tokens.csv
SELECT * FROM tokens;

.output wallet_tag_data_sources.csv
SELECT * FROM data_sources;
