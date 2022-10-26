w0 assigned a path var

MATCH w0=()-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25


w0 assigned a wallet

MATCH (w0)-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25
```

Arrow of time query (All txions within 10 block_numbers of matched t0)
```
MATCH p=(w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)
WHERE t0.block_number < t1.block_number < t0.block_number +10
RETURN p limit 25
```

Create index (maybe create index on wallet creation date?)
```
CREATE INDEX example_index_1 FOR (a:Actor) ON (a.name)
```

```
MATCH txns = ()-[tanx:*3]-()
RETURN txns LIMIT 25
```

```
MATCH paths = ()-[txns:TXN*3]->()
WHERE txns[0].block_number < txns[1].block_number < txns[2].block_number
  AND txns[0].token_address = txns[1].token_address = txns[2].token_address
RETURN paths LIMIT 10
```

# See all the txions in sequence
```
MATCH paths = ()-[txns:TXN*3]->()
WHERE txns[0].block_number < txns[1].block_number < txns[2].block_number
  AND txns[0].token_address = txns[1].token_address = txns[2].token_address
UNWIND txns AS t
RETURN t LIMIT 25
```


# Row number query (maybe)
```
MATCH (n:User)
WITH n
ORDER BY n.created_at
WITH collect(n) as users
UNWIND range(0, size(users)-1) as pos
SET (users[pos]).number = pos
```

# paths that obey arrow of time along with the
```
MATCH paths = (w0)-[txns:TXN*4]->(w1)
WHERE txns[0].block_number < txns[1].block_number < txns[2].block_number
  AND txns[0].token_address = txns[1].token_address = txns[2].token_address
UNWIND range(0, size(txns) - 1) AS step_number
RETURN step_number, txns[step_number].token, txns[step_number].block_number,  txns[step_number].num_tokens
LIMIT 25
```

# https://neo4j.com/developer/kb/comparing-relationship-properties-within-a-path/
```
MATCH path = (w0)-[txns:TXN * 10]->(w1)
WHERE w0.address = w1.address
  AND ALL(
    i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
  )
RETURN size(txns) AS path_length #, path,
LIMIT 5
```


## Cycle detection query - cycles of length at most 5, with txns made up of at least 10.0 tokens
```cypher
MATCH path = (w0)-[txns:TXN * 2..5]->(w1)
WHERE w0.address = w1.address
  AND ALL(txn in txns WHERE txn.num_tokens > 0.1)
  AND ALL(
    i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
  )
RETURN size(txns) AS path_length, path
LIMIT 1
```

Around 7000 blocks per day, so this is cycles within a day
```
MATCH path = (w0)-[txns:TXN *2..4]->(w1)
WHERE ALL(
        i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
  )
  AND ALL(txn in txns WHERE txn.num_tokens > 0.1)
  AND w0.address = w1.address
RETURN size(txns) AS path_length, path
LIMIT 1
```

## Cycles with txns in 24 hours increments, with no crossovers
```
MATCH path = (w0)-[txns:TXN *2..4]->(w1)
WHERE ALL(
        i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
      AND txns[i].END.address <> w0.address
      AND txns[i].START.address <> txns[i + 1].END.address
  )
  AND ALL(txn in txns WHERE txn.num_tokens > 0.1)
  AND w0.address = w1.address
RETURN size(txns) AS path_length, path
LIMIT 1
```


// celsius
```
MATCH path = (w0)-[txns:TXN *2..4]->(w1)
WHERE w0.address = '0xfa65be15f2f6c97b14adfcf1a2085c13d42c098d'
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
  )
  AND ALL(txn IN txns WHERE txn.num_tokens > 1.0)
UNWIND range(0, size(txns) - 1) AS i
CALL apoc.refactor.extractNode(txns[i], ['Wallet'], 'input', 'output')
YIELD input, output
RETURN i AS step, input, output
LIMIT 25
```


// Get paths out from possible celsius wallet
```
MATCH path = (w0)-[txns:TXN *5..6]->(w1)
WHERE w0.address = '0xfa65be15f2f6c97b14adfcf1a2085c13d42c098d'
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
  )
  AND ALL(txn IN txns WHERE txn.num_tokens > 1.0)
UNWIND range(0, size(txns) - 1) AS i
RETURN collect(
    [
      i,
      substring(nodes(path)[i].address, 0, 8) + '..',
      round(relationships(path)[i].num_tokens, 3)
    ]
  ) AS the_path,
  nodes(path)[-1].address AS final_destination
LIMIT 25
```


// Query paths from celsius
MATCH path = (w0)-[txns:TXN *3..6]->(w1)<-[other_txns:TXN *3..6]-(w0)
WHERE w0.address = '0xfa65be15f2f6c97b14adfcf1a2085c13d42c098d'
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + $num_blocks_between_hops
  )
  AND ALL(
        i IN range(0, size(other_txns) - 2, 2)  // Just make sure every other step is different
    WHERE other_txns[i].block_number < other_txns[i + 1].block_number
      AND other_txns[i + 1].block_number < other_txns[i].block_number + $num_blocks_between_hops
      // Only compare if the path is long enough
      AND CASE i < size(txns)
            WHEN true THEN txns[i] <> other_txns[i]
            ELSE true END
  )
  AND ALL(txn IN txns WHERE txn.num_tokens > 10.0)
  AND ALL(txn IN other_txns WHERE txn.num_tokens > 10.0)
UNWIND range(0, size(txns) - 1) AS i
RETURN collect(
    [
      i,
      substring(nodes(path)[i].address, 0, 8) + '..',
      round(relationships(path)[i].num_tokens, 3)
    ]
  ) AS the_path,
  nodes(path)[-1].address AS final_destination,
  size(other_txns) AS length_of_other_path
LIMIT 1


// Find wallets with < 10 total outbound txns
MATCH (w)-[txn]->()
WITH w.address as address, count(*) as c
WHERE c < 10
RETURN address, c
LIMIT 10


# Index
```
CREATE INDEX idx_block_number_num_tokens IF NOT EXISTS
FOR ()-[r:TXN]-()
ON (r.block_number, r.num_tokens)
```


// Permutations of size 2 or 3
MATCH (w)-[txn]->()
WHERE txn.num_tokens > 10
WITH w.address AS address, collect([txn.transactionID, txn.block_number, txn.num_tokens]) AS txns, count(*) AS c
WHERE c < 6
  AND c > 1
RETURN
  address,
  apoc.coll.combinations(txns, 2, CASE size(txns) > 3 WHEN true THEN 3 ELSE size(txns) END)
LIMIT 10


// Find permutations of txions that sum to a range
MATCH (w)-[txn]->()
WHERE txn.num_tokens > 10
WITH w.address AS address, collect([txn.transactionID, txn.block_number, txn.num_tokens]) AS txns, count(*) AS c
WHERE 8 > c > 1

WITH address AS address,
     apoc.coll.combinations(txns, 2, CASE size(txns) > 3 WHEN true THEN 3 ELSE size(txns) END) AS permutations
UNWIND permutations AS permutation

WITH address AS address, permutation AS txs, reduce(tokens = 0, t in permutation | tokens + t[2]) AS num_tokens
WHERE 100 > num_tokens > 50
RETURN address, txs, num_tokens
LIMIT 10


// Find wallets with between 2 and 20 outbound txns, then among those:
//    Find combinations of 2 to 4 txns that
//       a. happened within 70 blocks of each other
//       b. added up to between 99 and 101 eth
MATCH (w)-[txn]->()
WHERE txn.num_tokens > 10
  AND txn.block_number >= 3800000
 WITH w.address AS address,
      collect([txn.transactionID, txn.block_number, txn.num_tokens]) AS txns,
      count(*) AS c
WHERE 20 > c > 1

WITH address AS address,
     apoc.coll.combinations(txns, 2, CASE size(txns) > 4 WHEN true THEN 4 ELSE size(txns) END) AS permutations
UNWIND permutations AS permutation

WITH address AS address,
     permutation AS txns,
     reduce(tokens = 0, t in permutation | tokens + t[2]) AS num_tokens
WHERE 101 > num_tokens > 99
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE abs(txns[i][1] - txns[-1][1]) < 70
  )
RETURN address, txns, num_tokens
ORDER BY txns[0][1]
LIMIT 25


//Celsius (Mike Burgersburg)
MATCH path = (w0)-[txns:TXN * 2]->(w1)
WHERE w1.address = toLower('0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27')
  AND ALL(
        i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 70
  )
  AND ALL(txn in txns WHERE txn.num_tokens >= 1.0)

WITH txns AS txns,
     path AS path,
     apoc.coll.combinations(txns, 2, CASE size(txns) > 4 WHEN true THEN 4 ELSE size(txns) END) AS permutations
RETURN path
LIMIT 1


// Celsius questions from Mike: Who funded '0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27'?
:param blocks_to_check => 10000;  // How many blocks before the final txns will we search
:param txn_size => 1000;  // Aggregate size of 'cascaded' txions
:param tolerance => 2;  // how much distance +/- from txn_size will we consider part of the cascade
:param min_txns_in_cascade => 1;
:param max_txns_in_cascade => 3;  // Query run time will get more expensive with higher values
:param min_txn_size => 1; // Don't look at txns for less tokens than this number
:param address_length => 9; // Just for printing

MATCH path = ()-[tx1]->()-[tx2]->(celsius_wallet)
WHERE celsius_wallet.address = toLower('0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27')
  AND ALL(txn in [tx1, tx2] WHERE txn.num_tokens >= $min_txn_size)
  AND (tx2.block_number - $blocks_to_check) < tx1.block_number < tx2.block_number
WITH collect(DISTINCT tx1) AS txns, collect(DISTINCT tx2) AS final_txns

// Set max_txns bc if you call apoc.combo fxn with too high a max you get nulls
WITH txns AS txns,
     final_txns AS final_txns,
     CASE size(txns) > $max_txns_in_cascade WHEN true THEN $max_txns_in_cascade ELSE size(txns) END AS max_txns
WITH apoc.coll.combinations(txns, $min_txns_in_cascade, max_txns) AS txn_groups,
     final_txns AS final_txns
UNWIND txn_groups AS txn_group

WITH txn_group AS txn_group,
     reduce(tokens = 0, t in txn_group | tokens + t.num_tokens) AS num_tokens,
     final_txns AS final_txns
WHERE ($txn_size + $tolerance) > num_tokens > ($txn_size - $tolerance)
  AND ALL(
        i IN range(0, size(txn_group) - 2)
    WHERE abs(txn_group[i].block_number - txn_group[-1].block_number) < 50
  )
RETURN SUBSTRING(STARTNODE(txn_group[0]).address, 0, $address_length) AS from_wallet,
       [t in txn_group | [SUBSTRING(ENDNODE(t).address, 0, $address_length), '=>', ROUND(t.num_tokens, 2)]],
       num_tokens AS total_tokens,
       final_txns


// Attempt to generalize previous query
MATCH path = ()-[txns:TXN * 2]->(celsius_wallet)
WHERE celsius_wallet.address = toLower('0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27')
  AND ALL(t in txns WHERE t.num_tokens >= 1.0)
  AND (tx2.block_number - $blocks_to_check) < tx1.block_number < tx2.block_number
WITH collect(DISTINCT tx1) AS txns, collect(DISTINCT tx2) AS final_txns

// Set max_txns bc if you call apoc.combo fxn with too high a max you get nulls
WITH txns AS txns,
     final_txns AS final_txns,
     CASE size(txns) > $max_txns_in_cascade WHEN true THEN $max_txns_in_cascade ELSE size(txns) END AS max_txns
WITH apoc.coll.combinations(txns, $min_txns_in_cascade, max_txns) AS txn_groups,
     final_txns AS final_txns
UNWIND txn_groups AS txn_group

WITH txn_group AS txn_group,
     reduce(tokens = 0, t in txn_group | tokens + t.num_tokens) AS num_tokens,
     final_txns AS final_txns
WHERE ($txn_size + $tolerance) > num_tokens > ($txn_size - $tolerance)
  AND ALL(
        i IN range(0, size(txn_group) - 2)
    WHERE abs(txn_group[i].block_number - txn_group[-1].block_number) < 50
  )
RETURN SUBSTRING(STARTNODE(txn_group[0]).address, 0, $address_length) AS from_wallet,
       [t in txn_group | [SUBSTRING(ENDNODE(t).address, 0, $address_length), '=>', ROUND(t.num_tokens, 2)]],
       num_tokens AS total_tokens,
       final_txns
