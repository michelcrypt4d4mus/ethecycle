-- created_at,id,type,memo,from,to,amount,fee,token,successful

CREATE TABLE kag_txns (
  created_at TIMESTAMPTZ,
  id VARCHAR NOT NULL UNIQUE,
  record_type VARCHAR,
  memo VARCHAR,
  from_address VARCHAR,
  to_address VARCHAR,
  amount FLOAT,
  fee FLOAT,
  token VARCHAR,
  successful_string VARCHAR
);


\copy kag_txns
  FROM '/Users/syblius/Downloads/KAG.csv'
    CSV
    HEADER
    DELIMITER ',';


-- Biggest senders
SELECT
  from_address,
  ROUND(SUM(amount)::NUMERIC, 2) AS amount,
  ROUND(SUM(fee)::NUMERIC, 2) AS fee,
  COUNT(*) AS txn_count,
  ROUND(SUM(amount)::NUMERIC / COUNT(*), 2) AS avg_txn_amount,
  COUNT(DISTINCT(to_address)) AS unique_to_address_count
FROM kag_txns
GROUP BY 1
ORDER BY 2 DESC;

-- Biggest receivers
SELECT
  to_address,
  ROUND(SUM(amount)::NUMERIC, 2) AS amount,
  ROUND(SUM(fee)::NUMERIC, 2) AS fee,
  COUNT(*) AS txn_count,
  ROUND(SUM(amount)::NUMERIC / COUNT(*), 2) AS avg_txn_amount,
  COUNT(DISTINCT(from_address)) AS unique_from_address_count
FROM kag_txns
GROUP BY 1
ORDER BY 2 DESC;
