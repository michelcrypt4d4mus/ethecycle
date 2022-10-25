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
MATCH paths = ()-[txns:TXN*3]->()
WHERE txns[0].block_number < txns[1].block_number < txns[2].block_number
  AND txns[0].token_address = txns[1].token_address = txns[2].token_address
UNWIND range(0, size(txns) - 1) AS step_number
RETURN step_number, txns[step_number].token, txns[step_number].block_number,  txns[step_number].num_tokens
LIMIT 25
```
