-- Aggregate by minute/token/from_address
WITH outbound_txns AS (
  SELECT
    `from` AS from_address,
    `to` AS to_address,
    contract_address,
    DATE_TRUNC('minute', evt_block_time) AS minute,
    SUM(value) AS outbound_value,
    COUNT(*) AS txn_count
  FROM erc20_ethereum.evt_Transfer
  WHERE evt_block_time > '2022-11-08T15:03:00'
    AND `from` IN (
        '0xd2e334a566279a7d7858c85dde27e31e14130fb0',
        '0xc99d7688a4e0e9ba6a3491e7d175c9abcd914f93',
        '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2',
        '0xc098b2a3aa256d2140208c3de6543aaef5cd3a94',
        '0x68eb95dc9934e19b86687a10df8e364423240e94',
        '0x871baed4088b863fd6407159f3672d70cd34837d',
        '0x016ee7373248a80bde1fd6baa001311d233b3cfa',
        '0x2f5e2c9002c058c063d21a06b6cabb50950130c8',
        '0x50d1c9771902476076ecfc8b2a83ad6b9355a4c9',
        '0x54dda22ae140edb605c73073eabb6f4aea2fc237',
        '0xe31a9498a22493ab922bc0eb240313a46525ee0a',
        '0x712d0f306956a6a4b4f9319ad9b9de48c5345996',
        '0x93c08a3168fc469f3fc165cd3a471d19a37ca19e',
        '0xca436e14855323927d6e6264470ded36455fc8bd',
        '0x83a127952d266a6ea306c40ac62a4a70668fe3bd',
        '0xc5ed2333f8a2c351fca35e5ebadb2a82f5d254c3',
        '0x89183c0a8965c0299997be9af700a801bdccc2da',
        '0xe5d0ef77aed07c302634dc370537126a2cd26590',
        '0x5d13f4bf21db713e17e04d711e0bf7eaf18540d6',
        '0x882a812d75aee53efb8a144f984b258b6c4807f0',
        '0xbefe4f86f189c1c817446b71eb6ac90e3cb68e60',
        '0xb78e90e2ec737a2c0a24d68a0e54b410fff3bd6b',
        '0x964d9d1a532b5a5daeacbac71d46320de313ae9c',
        '0xfa453aec042a837e4aebbadab9d4e25b15fad69d',
        '0x4deb3edd991cfd2fcdaa6dcfe5f1743f6e7d16a6',
        '0x477573f212a7bdd5f7c12889bd1ad0aa44fb82aa',
        '0xce31190a03fc3c5f23167e88e75066824823222d',
        '0x60009b78da046ac64ef789c29ca05b79cdf73c10',
        '0x73c0ae50756c7921d1f32ada71b8e50c5de7ff9c',
        '0x60ae578abdfded1fb0555f54148fdd7b400a34ed',
        '0xa726c00cda1f60aaab19bc095d02a46556837f31',
        '0xa6e683d5dccce898f16bb48071f08f2304c8ba09',
        '0x0c0fe4e0236480e16b679ee1fd0c5247f9cf35f0',
        '0x0f4ee9631f4be0a63756515141281a3e2b293bbe',
        '0x97137466bc8018531795217f0ecc4ba24dcba5c1',
        '0x84d34f4f83a87596cd3fb6887cff8f17bf5a7b83',
        '0x78835265ac857bf3420830c71987b1a55f73c2dc',
        '0x4c8cfe078a5b989cea4b330197246ced82764c63',
        '0x7cc549cdef7248c11a84d718fd25eafb57d8d614',
        '0x073dca8acbc11ffb0b5ae7ef171e4c0b065ffa47',
        '0x3507e4978e0eb83315d20df86ca0b976c0e40ccb'
    )
  GROUP BY 1,2,3,4
)

SELECT
    from_address,
    LEFT(get_labels(from_address), 35) AS from_label_short,
    to_address,
    LEFT(get_labels(to_address), 35) AS to_label_short,
    usd.symbol,
    SUM(usd.price * outbound_value) / power(10, FIRST(usd.decimals)) AS outbound_usd,
    MIN(outbound_txns.minute) AS first_txn_at,
    MAX(outbound_txns.minute) AS last_txn_at,
    SUM(txn_count) AS outbound_txn_count,
    get_labels(from_address) AS from_labels_full,
    get_labels(to_address) AS to_labels_full
FROM outbound_txns
INNER JOIN prices.usd
        ON usd.blockchain = 'ethereum'
       AND usd.contract_address = outbound_txns.contract_address
       AND usd.minute = outbound_txns.minute
GROUP BY 1,2,3,4,5,10,11
HAVING SUM(usd.price * outbound_value) / power(10, FIRST(usd.decimals)) > {{minimum_txn_usd}}
ORDER BY 1 DESC
