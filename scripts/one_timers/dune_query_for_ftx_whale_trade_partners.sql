WITH ftx_transfers AS (
    SELECT
      `from` AS from_address,
      `to` AS to_address,
      usd.contract_address,
      usd.blockchain,
      usd.minute,
      FIRST(usd.price * value / power(10, usd.decimals)) AS amount_usd
    FROM erc20_ethereum.evt_Transfer
      INNER JOIN prices.usd
              ON usd.contract_address = evt_Transfer.contract_address
             AND usd.blockchain = 'ethereum'
             AND usd.minute = DATE_TRUNC('minute', evt_block_time)
    WHERE `from` IN (
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x7abe0ce388281d2acf297cb089caef3819b13448'
       )
       OR `to` IN (
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x7abe0ce388281d2acf297cb089caef3819b13448'
       )
     GROUP BY 1,2,3,4,5
),

big_partners AS (
  SELECT
    CASE
      WHEN from_address IN ('0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2', '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94', '0x7abe0ce388281d2acf297cb089caef3819b13448') THEN
        'outbound'
      ELSE
        'inbound'
      END AS direction,

    CASE
      WHEN from_address IN ('0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2', '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94', '0x7abe0ce388281d2acf297cb089caef3819b13448') THEN
        to_address
      ELSE
        from_address
      END AS wallet_address,

    ROUND(SUM(amount_usd)) AS amount_usd,
    COUNT(*) AS txn_count
  FROM ftx_transfers
  GROUP BY 1,2
  ORDER BY 3 DESC
  LIMIT 500
)

SELECT
  wallet_address,
  direction,
  amount_usd,
  txn_count,
  amount_usd / txn_count AS avg_usd_per_txn
FROM big_partners
WHERE wallet_address NOT IN ('0xa00b0540f43e00a634d016a31b0a39d95170e6bf')
ORDER BY 3 DESC
