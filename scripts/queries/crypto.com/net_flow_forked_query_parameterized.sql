with address as (select address, label
                 from (values
                      ('0x72A53cDBBcc1b9efa39c834A540550e23463AAcB', 'Crypto.com 1'),
                      ('0x46340b20830761efd32832a74d7169b29feb9758', 'Crypto.com 2'),
                      ('0xcffad3200574698b78f32232aa9d63eabd290703', 'Crypto.com 3'),
                      ('0x7758e507850da48cd47df1fb5f875c23e3340c50', 'Crypto.com 4'),
                      ('0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', 'CRONOS Token'),
                      ('0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3', 'Crypto.com 5'),
                      ('0xb63b606ac810a52cca15e44bb630fd42d8d1d83d', 'Crypto.com: MCO Token')
                          ) as t( address, label)),
     ethereum_token_flow as (
         with erc20_token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_ethereum.evt_Transfer
             WHERE `from` in (select address from address)
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_ethereum.evt_Transfer
             WHERE `to` in (select address from address )
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
              eth_flow as (
                  select block_time,
                         date_trunc('day', block_time) as block_day,
                         - value / 1e18                as amount
                  from ethereum.transactions
                  WHERE `from` in (select address from address )
                    AND `to` NOT in (select address from address)
                    and block_time >= '{{net_flow_start_date}}'
                  union all
                  select block_time,
                         date_trunc('day', block_time) as block_day,
                         value / 1e18                  as amount
                  from ethereum.transactions
                  WHERE `to` in (select address from address)
                    AND `from` NOT in (select address from address)
                    and block_time >= '{{net_flow_start_date}}'
              ),
              price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'ethereum'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )

         select *
         from (select block_date,
                      erc20.token_address,
                      p.symbol,
                      sum(amount / power(10, p.decimals))               as amount,
                      sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
               from erc20_token_flow as erc20
                        left join price as p
                                  on erc20.token_address = p.token_address and erc20.block_date = p.price_day
               where p.token_address is not null
               group by 1, 2, 3
               union all
               select e.block_day,
                      ''                      as token_address,
                      'ETH'                   as symbol,
                      sum(amount)             as amount,
                      sum(amount * avg_price) as amount_usd
               from eth_flow as e
                        left join price as p on e.block_day = p.price_day and p.symbol = 'WETH'
               group by 1, 2, 3)
     ),
     polygon_token_flow as (
         with token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_polygon.evt_Transfer
             WHERE `from` in (select address from address)
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_polygon.evt_Transfer
             WHERE `to` in (select address from address)
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
              price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'polygon'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )
         select block_date,
                f.token_address,
                p.symbol,
                sum(amount / power(10, p.decimals))               as amount,
                sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
         from token_flow as f
                  left join price as p
                            on f.token_address = p.token_address and f.block_date = p.price_day
         group by 1, 2, 3
     ),
     optimism_token_flow(
                         with token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_optimism.evt_Transfer
             WHERE `from` in (select address from address)
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_optimism.evt_Transfer
             WHERE `to` in (select address from address )
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
                         price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'optimism'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )
         select block_date,
         f.token_address,
                p.symbol,
                         sum(amount / power(10, p.decimals))               as amount,
                         sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
         from token_flow as f
                  left join price as p
                            on f.token_address = p.token_address and f.block_date = p.price_day
         group by 1, 2, 3
         ),
     arbitrum_token_flow(
                         with token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_arbitrum.evt_Transfer
             WHERE `from` in (select address from address)
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_arbitrum.evt_Transfer
             WHERE `to` in (select address from address)
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
                         price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'arbitrum'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )
         select block_date,
         f.token_address,
                p.symbol,
                         sum(amount / power(10, p.decimals))               as amount,
                         sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
         from token_flow as f
                  left join price as p
                            on f.token_address = p.token_address and f.block_date = p.price_day
         group by 1, 2, 3
         ),
     bnb_token_flow(
                    with token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_bnb.evt_Transfer
             WHERE `from` in (select address from address )
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_bnb.evt_Transfer
             WHERE `to` in (select address from address )
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
                    price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'bnb'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )
         select block_date,
         f.token_address,
                p.symbol,
                    sum(amount / power(10, p.decimals))               as amount,
                    sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
         from token_flow as f
                  left join price as p
                            on f.token_address = p.token_address and f.block_date = p.price_day
         group by 1, 2, 3
         ),
     avalanche_token_flow(
                          with token_flow as (
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    - value                           as amount
             FROM erc20_avalanche_c.evt_Transfer
             WHERE `from` in (select address from address )
               AND `to` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
             union all
             SELECT contract_address                  as token_address,
                    evt_block_time,
                    date_trunc('day', evt_block_time) as block_date,
                    value                             as amount
             FROM erc20_avalanche_c.evt_Transfer
             WHERE `to` in (select address from address)
               AND `from` NOT in (select address from address)
               and evt_block_time >= '{{net_flow_start_date}}'
         ),
                          price as (
                  SELECT date_trunc('day', minute) as price_day,
                         contract_address          as token_address,
                         decimals,
                         symbol,
                         avg(price)                as avg_price
                  FROM prices.usd
                  where blockchain = 'avalanche_c'
                    and minute >= '{{net_flow_start_date}}'
                  GROUP BY 1, 2, 3, 4
              )
         select block_date,
         f.token_address,
                p.symbol,
                          sum(amount / power(10, p.decimals))               as amount,
                          sum(amount / power(10, p.decimals) * p.avg_price) as amount_usd
         from token_flow as f
                  left join price as p
                            on f.token_address = p.token_address and f.block_date = p.price_day
         group by 1, 2, 3
         ),
     final as (
         select *
         from ethereum_token_flow
         union all
         select *
         from polygon_token_flow
         union all
         select *
         from optimism_token_flow
         union all
         select *
         from arbitrum_token_flow
         union all
         select *
         from bnb_token_flow
         union all
         select *
         from avalanche_token_flow)

select block_date, sum(amount_usd) as amount_usd
from final
where symbol is not null
  and amount is not null
  and amount not between -1 and 1
group by 1
order by 1 desc
