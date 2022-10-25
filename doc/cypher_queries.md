

w0 assigned a path var

```
MATCH w0=()-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25
```

w0 assigned a wallet
```
MATCH (w0)-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25
```

Arrow of time query
```
MATCH (w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)
WHERE t0.block_number < t1.block_number
RETURN t0, t1 limit 25
```
