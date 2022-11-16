WITH address AS (
  SELECT
    address,
    label
  from (
    values
      ('0x72A53cDBBcc1b9efa39c834A540550e23463AAcB', 'Crypto.com 1'),
      ('0x46340b20830761efd32832a74d7169b29feb9758', 'Crypto.com 2'),
      ('0xcffad3200574698b78f32232aa9d63eabd290703', 'Crypto.com 3'),
      ('0x7758e507850da48cd47df1fb5f875c23e3340c50', 'Crypto.com 4'),
      ('0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', 'CRONOS Token'),
      ('0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3', 'Crypto.com 5'),
      ('0xb63b606ac810a52cca15e44bb630fd42d8d1d83d', 'Crypto.com: MCO Token')
  ) AS t(address, label)
),

prices_ethereum AS (
  SELECT
    COALESCE(blockchain, 'ethereum') AS blockchain,
    date_trunc('minute', minute) AS price_minute,
    contract_address,
    decimals,
    symbol,
    avg(price) AS avg_price
  FROM prices.usd
  where (blockchain = 'ethereum' OR blockchain IS NULL)
    and minute >= '{{net_flow_start_date}}'
  GROUP BY 1, 2, 3, 4, 5
),

prices_polygon AS (
  SELECT
    COALESCE(blockchain, 'polygon') AS blockchain,
    date_trunc('minute', minute) AS price_minute,
    contract_address,
    decimals,
    symbol,
    avg(price) AS avg_price
  FROM prices.usd
  where (blockchain = 'polygon' OR blockchain IS NULL)
    and minute >= '{{net_flow_start_date}}'
  GROUP BY 1, 2, 3, 4, 5
),

prices_by_minute AS (
  SELECT * FROM prices_ethereum
  UNION ALL
  SELECT * FROM prices_polygon
),


ethereum_flow AS (
  SELECT
    'ethereum'  AS blockchain,
    contract_address,
    date_trunc('minute', evt_block_time) AS block_minute,
    -value AS amount
  FROM erc20_ethereum.evt_Transfer
    INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
      LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
  WHERE to_address.address IS NULL  -- Negative join
    and evt_block_time >= '{{net_flow_start_date}}'

  UNION ALL

  SELECT
    'ethereum' AS blockchain,
    contract_address,
    date_trunc('minute', evt_block_time) AS block_minute,
    value AS amount
  FROM erc20_ethereum.evt_Transfer
    INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
      LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
  WHERE from_address.address IS NULL  -- Negative join
    and evt_block_time >= '{{net_flow_start_date}}'

  UNION ALL

--  eth_flow AS (
  SELECT
    'ethereum'  AS blockchain,
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' AS contract_address, -- WETH
    date_trunc('minute', block_time) AS block_minute,
    -value / 1e18                AS amount
  from ethereum.transactions
    INNER JOIN address AS from_address ON from_address.address = transactions.`from`
     LEFT JOIN address AS to_address ON to_address.address == transactions.`to`
  WHERE to_address.address IS NULL  -- Negative join
    AND success
    and block_time >= '{{net_flow_start_date}}'

  UNION ALL

  SELECT
    'ethereum'  AS blockchain,
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2' AS contract_address, -- WETH
    date_trunc('minute', block_time) AS block_minute,
    value / 1e18                  AS amount
  from ethereum.transactions
    INNER JOIN address AS to_address ON to_address.address == transactions.`to`
     LEFT JOIN address AS from_address ON from_address.address = transactions.`from`
  WHERE from_address.address IS NULL  -- Negative join
    AND success
    and block_time >= '{{net_flow_start_date}}'
),


polygon_token_flow AS (
    SELECT
      'polygon' AS blockchain,
      contract_address,
      date_trunc('minute', evt_block_time) AS block_minute,
      -value AS amount
    FROM erc20_polygon.evt_Transfer
      INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
       LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
    WHERE to_address.address IS NULL  -- Negative join
      AND evt_block_time >= '{{net_flow_start_date}}'

    UNION ALL

    SELECT
      'polygon' AS blockchain,
      contract_address,
      date_trunc('minute', evt_block_time) AS block_minute,
      value AS amount
    FROM erc20_polygon.evt_Transfer
      INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
       LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
    WHERE from_address.address IS NULL  -- Negative join
      and evt_block_time >= '{{net_flow_start_date}}'
  ),


final AS (
  SELECT * from ethereum_flow
  UNION ALL
  SELECT * from polygon_token_flow
)

SELECT
  final.blockchain,
  DATE(final.block_minute),
  SUM(amount / power(10, p.decimals)) AS amount,
  SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd
  --SUM(CASE WHEN final.blockchain = 'ethereum' THEN COALESCE(amount / power(10, p.decimals) * p.avg_price), 0) ELSE 0 END) AS ethereum_net_usd,
  --SUM(CASE WHEN final.blockchain = 'polygon' THEN COALESCE(amount / power(10, p.decimals) * p.avg_price), 0) ELSE 0 END) AS polygon_net_usd,
  --SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
  --SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
FROM final
  INNER JOIN prices_by_minute AS p
          ON p.contract_address = final.contract_address
         AND p.price_minute = final.block_minute
         AND p.blockchain = final.blockchain
WHERE symbol is not null
  AND amount is not null
  --and amount not between -1 and 1
GROUP BY 1,2
ORDER BY 2 DESC, 1



  -- SELECT
  --   blockchain,
  --   date_trunc('day', block_minute) AS block_date,
  --   p.symbol,
  --   SUM(amount / power(10, p.decimals)) AS amount,
  --   SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
  --   SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
  --   SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
  -- FROM erc20_token_flow AS erc20
  --   INNER JOIN price AS p
  --           ON erc20.token_address = p.token_address
  --          AND erc20.block_minute = p.price_minute
  -- GROUP BY 1, 2, 3
-- ),


-- optimism_token_flow AS (
--   with erc20_token_flow AS (
--     SELECT
--       'optimism'  AS blockchain,
--       contract_address AS token_address,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       -value AS amount
--     FROM erc20_optimism.evt_Transfer
--       INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--        LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE to_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'

--     UNION ALL

--     SELECT
--       'optimism'  AS blockchain,
--       contract_address AS token_address,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       value AS amount
--     FROM erc20_optimism.evt_Transfer
--       INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--        LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--     WHERE from_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'
--   ),

--   price AS (
--     SELECT
--       date_trunc('minute', minute) AS price_minute,
--       contract_address AS token_address,
--       decimals,
--       symbol,
--       avg(price) AS avg_price
--     FROM prices.usd
--     where blockchain = 'optimism'
--       and minute >= '{{net_flow_start_date}}'
--     GROUP BY 1, 2, 3, 4
--   )

--   SELECT
--     blockchain,
--     date_trunc('day', block_minute) AS block_date,
--     p.symbol,
--     SUM(amount / power(10, p.decimals)) AS amount,
--     SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
--     SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
--     SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
--   from erc20_token_flow AS erc20
--     INNER JOIN price AS p
--             on erc20.token_address = p.token_address
--            and erc20.block_minute = p.price_minute
--   group by 1, 2, 3
-- ),



-- arbitrum_token_flow AS (
--   with erc20_token_flow AS (
--     SELECT
--       'arbitrum'  AS blockchain,
--       contract_address AS token_address,
--       evt_block_time,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       -value AS amount
--     FROM erc20_arbitrum.evt_Transfer
--       INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--        LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE to_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'

--     UNION ALL

--     SELECT
--       'arbitrum'  AS blockchain,
--       contract_address AS token_address,
--           evt_block_time,
--           date_trunc('minute', evt_block_time) AS block_minute,
--           value AS amount
--     FROM erc20_arbitrum.evt_Transfer
--        LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--       INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE from_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'
--   ),

--   price AS (
--     SELECT
--       date_trunc('minute', minute) AS price_minute,
--       contract_address AS token_address,
--       decimals,
--       symbol,
--       avg(price) AS avg_price
--     FROM prices.usd
--     where blockchain = 'arbitrum'
--       and minute >= '{{net_flow_start_date}}'
--     GROUP BY 1, 2, 3, 4
--   )

--   SELECT
--     blockchain,
--     date_trunc('day', block_minute) AS block_date,
--     p.symbol,
--     SUM(amount / power(10, p.decimals)) AS amount,
--     SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
--     SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
--     SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
--   from erc20_token_flow AS erc20
--     INNER JOIN price AS p
--             on erc20.token_address = p.token_address
--            and erc20.block_minute = p.price_minute
--   group by 1, 2, 3
-- ),




-- bnb_token_flow AS (
--   with erc20_token_flow AS (
--     SELECT
--       'bnb'  AS blockchain,
--       contract_address AS token_address,
--       evt_block_time,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       -value AS amount
--     FROM erc20_bnb.evt_Transfer
--       INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--        LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE to_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'

--     UNION ALL

--     SELECT
--       'bnb'  AS blockchain,
--       contract_address AS token_address,
--       evt_block_time,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       value AS amount
--     FROM erc20_bnb.evt_Transfer
--        LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--       INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE from_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'
--   ),

--   price AS (
--     SELECT
--       date_trunc('minute', minute) AS price_minute,
--       contract_address AS token_address,
--       decimals,
--       symbol,
--       avg(price) AS avg_price
--     FROM prices.usd
--     where blockchain = 'bnb'
--       and minute >= '{{net_flow_start_date}}'
--     GROUP BY 1, 2, 3, 4
--   )

--   SELECT
--     blockchain,
--     date_trunc('day', block_minute) AS block_date,
--     p.symbol,
--     SUM(amount / power(10, p.decimals)) AS amount,
--     SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
--     SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
--     SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
--   from erc20_token_flow AS erc20
--     INNER JOIN price AS p
--             on erc20.token_address = p.token_address
--            and erc20.block_minute = p.price_minute
--   group by 1, 2, 3
-- ),



-- avalanche_token_flow AS (
--   with erc20_token_flow AS (
--     SELECT
--       'avalanche'  AS blockchain,
--       contract_address AS token_address,
--       evt_block_time,
--       date_trunc('minute', evt_block_time) AS block_minute,
--       -value AS amount
--     FROM erc20_avalanche_c.evt_Transfer
--       INNER JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--        LEFT JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE to_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'

--     UNION ALL

--     SELECT
--       'avalanche'  AS blockchain,
--       contract_address AS token_address,
--           evt_block_time,
--           date_trunc('minute', evt_block_time) AS block_minute,
--           value AS amount
--     FROM erc20_avalanche_c.evt_Transfer
--        LEFT JOIN address AS from_address ON from_address.address = evt_Transfer.`from`
--       INNER JOIN address AS to_address ON to_address.address == evt_Transfer.`to`
--     WHERE from_address.address IS NULL  -- Negative join
--       and evt_block_time >= '{{net_flow_start_date}}'
--   ),

--   price AS (
--     SELECT
--       date_trunc('minute', minute) AS price_minute,
--       contract_address AS token_address,
--       decimals,
--       symbol,
--       avg(price) AS avg_price
--     FROM prices.usd
--     where blockchain = 'avalanche_c'
--       and minute >= '{{net_flow_start_date}}'
--     GROUP BY 1, 2, 3, 4
--   )

--   SELECT
--     blockchain,
--     date_trunc('day', block_minute) AS block_date,
--     p.symbol,
--     SUM(amount / power(10, p.decimals)) AS amount,
--     SUM(amount / power(10, p.decimals) * p.avg_price) AS amount_usd,
--     SUM(CASE WHEN amount >= 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS inbound_usd,
--     SUM(CASE WHEN amount < 0 THEN amount * p.avg_price / power(10, p.decimals) ELSE 0 END) AS outbound_usd
--   from erc20_token_flow AS erc20
--     INNER JOIN price AS p
--             on erc20.token_address = p.token_address
--            and erc20.block_minute = p.price_minute
--   where p.token_address is not null
--   group by 1, 2, 3
-- ),
