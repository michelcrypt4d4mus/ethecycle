WITH addresses AS (
    SELECT blockchain, address FROM tokens
    UNION ALL
    SELECT blockchain, address FROM wallets
)

SELECT
  blockchain,
  COUNT(DISTINCT address) AS unique_chain_addresses
FROM addresses
GROUP BY 1
ORDER BY 2 DESC
