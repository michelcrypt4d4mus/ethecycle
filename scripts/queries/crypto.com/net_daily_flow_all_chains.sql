with address as (
  select
    address,
    label
  from (values
      ('0x72A53cDBBcc1b9efa39c834A540550e23463AAcB', 'Crypto.com 1'),
      ('0x46340b20830761efd32832a74d7169b29feb9758', 'Crypto.com 2'),
      ('0xcffad3200574698b78f32232aa9d63eabd290703', 'Crypto.com 3'),
      ('0x7758e507850da48cd47df1fb5f875c23e3340c50', 'Crypto.com 4'),
      ('0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', 'CRONOS Token'),
      ('0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3', 'Crypto.com 5'),
      ('0xb63b606ac810a52cca15e44bb630fd42d8d1d83d', 'Crypto.com: MCO Token')
  ) as t(address, label)
),

ethereum_token_flow as (
  with erc20_token_flow as (
    SELECT
      'ethereum'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_ethereum.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'ethereum'  AS blockchain,
        contract_address                  as token_address,
        evt_block_time,
        date_trunc('minute', evt_block_time) as block_date,
        value                             as amount
    FROM erc20_ethereum.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  eth_flow as (
    select block_time,
            'ethereum'  AS blockchain,
            date_trunc('minute', block_time) as block_day,
            -value / 1e18                as amount
    from ethereum.transactions
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and block_time >= '{{net_flow_start_date}}'

    union all

    select block_time,
            'ethereum'  AS blockchain,
            date_trunc('minute', block_time) as block_day,
            value / 1e18                  as amount
    from ethereum.transactions
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'ethereum'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4

  UNION ALL

  select
    blockchain,
    e.block_day,
    '0x0'                      as token_address,
    'ETH'                   as symbol,
    sum(amount)             as amount,
    sum(amount * avg_price) as amount_usd
  from eth_flow as e
      LEFT JOIN price as p on e.block_day = p.price_day and p.symbol = 'WETH'
  group by 1, 2, 3,4
),

polygon_token_flow as (
  with erc20_token_flow as (
    SELECT
      'polygon'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_polygon.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'polygon'  AS blockchain,
      contract_address                  as token_address,
          evt_block_time,
          date_trunc('minute', evt_block_time) as block_date,
          value                             as amount
    FROM erc20_polygon.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'polygon'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4
),


optimism_token_flow as (
  with erc20_token_flow as (
    SELECT
      'optimism'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_optimism.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'optimism'  AS blockchain,
      contract_address                  as token_address,
          evt_block_time,
          date_trunc('minute', evt_block_time) as block_date,
          value                             as amount
    FROM erc20_optimism.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'optimism'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4
),



arbitrum_token_flow as (
  with erc20_token_flow as (
    SELECT
      'arbitrum'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_arbitrum.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'arbitrum'  AS blockchain,
      contract_address                  as token_address,
          evt_block_time,
          date_trunc('minute', evt_block_time) as block_date,
          value                             as amount
    FROM erc20_arbitrum.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'arbitrum'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4
),




bnb_token_flow as (
  with erc20_token_flow as (
    SELECT
      'bnb'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_bnb.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'bnb'  AS blockchain,
      contract_address                  as token_address,
          evt_block_time,
          date_trunc('minute', evt_block_time) as block_date,
          value                             as amount
    FROM erc20_bnb.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'bnb'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4
),



avalanche_token_flow as (
  with erc20_token_flow as (
    SELECT
      'avalanche'  AS blockchain,
      contract_address                  as token_address,
      evt_block_time,
      date_trunc('minute', evt_block_time) as block_date,
      -value                           as amount
    FROM erc20_avalanche.evt_Transfer
    WHERE `from` in (select address from address)
      AND `to` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'

    union all

    SELECT
      'avalanche'  AS blockchain,
      contract_address                  as token_address,
          evt_block_time,
          date_trunc('minute', evt_block_time) as block_date,
          value                             as amount
    FROM erc20_avalanche.evt_Transfer
    WHERE `to` in (select address from address)
      AND `from` NOT IN (select address from address)
      and evt_block_time >= '{{net_flow_start_date}}'
  ),

  price as (
    SELECT date_trunc('minute', minute) as price_day,
            contract_address          as token_address,
            decimals,
            symbol,
            avg(price)                as avg_price
    FROM prices.usd
    where blockchain = 'avalanche_c'
      and minute >= '{{net_flow_start_date}}'
    GROUP BY 1, 2, 3, 4
  )

  select
    blockchain,
    block_date,
    erc20.token_address,
    p.symbol,
    sum(amount / power(10, p.decimals))               as amount,
    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
  from erc20_token_flow as erc20
    LEFT JOIN price as p
            on erc20.token_address = p.token_address and erc20.block_date = p.price_day
  where p.token_address is not null
  group by 1, 2, 3,4
),


final as (
  select * from ethereum_token_flow
  union all
  select * from polygon_token_flow
  union all
  select * from optimism_token_flow
  UNION ALL
  SELECT * FROM arbitrum_token_flow
  UNION ALL
  SELECT * FROM bnb_token_flow
  UNION ALL
  SELECT * FROM avalanche_token_flow
)

select
  blockchain,
  block_date,
  SUM(CASE WHEN blockchain = 'ethereum' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS ethereum_net_usd,
  SUM(CASE WHEN blockchain = 'polygon' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS polygon_net_usd,
  SUM(CASE WHEN blockchain = 'optimism' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS optimism_net_usd,
  SUM(CASE WHEN blockchain = 'arbitrum' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS arbitrum_net_usd,
  SUM(CASE WHEN blockchain = 'bnb' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS bnb_net_usd,
  SUM(CASE WHEN blockchain = 'avalanche' THEN COALESCE(amount_usd, 0) ELSE 0 END) AS avalanche_net_usd
from final
where symbol is not null
  and amount is not null
  and amount not between -1 and 1
group by 1,2
order by 1,2 desc
