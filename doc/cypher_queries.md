w0 assigned a path var
```
MATCH w0=()-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25
```

w0 assigned a wallet
```
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

## There's around 7000 blocks per day, so this is cycles within a day
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



MATCH path = (w0)-[txns:TXN *2..4]->(w1)
WHERE w0.address = '0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27'
  AND ALL(
        i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
      AND txns[i].END.address <> w0.address
      AND txns[i].START.address <> txns[i + 1].END.address
  )
  AND ALL(txn in txns WHERE txn.num_tokens > 1.0)
RETURN size(txns) AS path_length, path
LIMIT 1



# celsius
```
MATCH path = (w0)-[txns:TXN *2..4]->(w1)
WHERE w0.address = '0xfa65be15f2f6c97b14adfcf1a2085c13d42c098d'
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
      AND txns[i + 1].block_number < txns[i].block_number + 7000
  )
  AND ALL(txn in txns WHERE txn.num_tokens > 1.0)
UNWIND range(0, size(txns) - 2, 2) AS i
RETURN i, txns[i], CASE i+1 > size(txns) - 1
                             WHEN true THEN 'END'
                             ELSE txns[i+1].num_tokens END AS tokens
LIMIT 25
```




# Index
```
CREATE INDEX idx_block_number_num_tokens IF NOT EXISTS
FOR ()-[r:TXN]-()
ON (r.block_number, r.num_tokens)
```
