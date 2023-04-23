// Make sure sidebar is on

// Single path
MATCH p = ()-[t0:TXN]->()-[t1:TXN]->() RETURN p LIMIT 1

// Simple cycle attempt - returns 2 exchanges going back and forth
MATCH p = (w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)-[t2:TXN]->(w3)-[t3:TXN]->(w4)
WHERE w0.address = w4.address
RETURN p LIMIT 1

// So we make sure the middle wallets are not the same
MATCH p = (w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)-[t2:TXN]->(w3)-[t3:TXN]->(w4)
WHERE w0.address = w4.address
  AND w2.address <> w0.address
  AND w3.address <> w1.address
  AND w3.address <> w0.address
  AND w4.address <> w2.address
  AND w4.address <> w1.address
  AND t0.num_tokens = t1.num_tokens = t2.num_tokens = t3.num_tokens
RETURN p LIMIT 1


// Table view
MATCH p = (w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)-[t2:TXN]->(w3)-[t3:TXN]->(w4)
WHERE w0.address = w4.address
  AND w2.address <> w0.address
  AND w3.address <> w1.address
  AND w3.address <> w0.address
  AND w4.address <> w2.address
  AND w4.address <> w1.address
  AND t0.num_tokens = t1.num_tokens = t2.num_tokens = t3.num_tokens
RETURN w0.address,t0.num_tokens,w1.address,t1.num_tokens,w2.address,t2.num_tokens,w3.address,t3.num_tokens,w4.address
LIMIT 1



// Follow the hacsker coins
MATCH p = (w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)-[t2:TXN]->(w3)-[t3:TXN]->(w4)
WHERE w0.category = 'hackers'
  AND (w4.category = 'cex' OR w3.category = 'cex')
  AND w2.address <> w0.address
  AND w3.address <> w1.address
  AND w3.address <> w0.address
  AND w4.address <> w2.address
  AND w4.address <> w1.address
  AND t0.num_tokens = t1.num_tokens = t2.num_tokens = t3.num_tokens
RETURN p
LIMIT 1
