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


-- Load data
\copy kag_txns
  FROM '/Users/uz0r/Downloads/KAG.csv'
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


-- Current balances
WITH sent_amounts AS (
  SELECT
    from_address,
    ROUND(SUM(amount)::NUMERIC, 2) AS sent_amount,
    ROUND(SUM(fee)::NUMERIC, 2) AS sent_fee,
    COUNT(*) AS sent_txn_count
  FROM kag_txns
  GROUP BY 1
),

received_amounts AS (
    SELECT
      to_address,
      ROUND(SUM(amount)::NUMERIC, 2) AS received_amount,
      COUNT(*) AS received_txn_count
    FROM kag_txns
    GROUP BY 1
)

SELECT
  COALESCE(to_address, from_address) AS address,
  COALESCE(received_amount, 0.0) - COALESCE(sent_amount, 0.0) - COALESCE(sent_fee, 0.0) AS current_balance,
  COALESCE(received_amount, 0.0) + COALESCE(sent_amount, 0.0) AS gross_txn_amount,
  COALESCE(received_amount, 0.0) AS in_amount,
  COALESCE(sent_amount, 0.0) AS out_amount,
  COALESCE(sent_fee, 0.0) AS fees,
  COALESCE(sent_txn_count, 0) AS out_txn_count,
  COALESCE(received_txn_count, 0) AS in_txn_count,
  COALESCE(sent_txn_count, 0) + COALESCE(received_txn_count, 0) AS gross_txn_count
FROM received_amounts
  FULL OUTER JOIN sent_amounts
               ON received_amounts.to_address = sent_amounts.from_address
ORDER BY 2 DESC

