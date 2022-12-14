// Cypher query style guide: https://s3.amazonaws.com/artifacts.opencypher.org/M20/docs/style-guide.pdf

// w0 assigned a path var
MATCH w0=()-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25


// w0 assigned a wallet
MATCH (w0)-[t0:TXN]->()-[t1:TXN]->() return w0,t0, t1 limit 25


// Find wallets with < 10 total outbound txns
MATCH (w)-[txn]->()
WITH w.address as address, count(*) as c
WHERE c < 10
RETURN address, c
LIMIT 10


// Top 100 eth sending wallets
// MATCH (w)-[txn]->()
// Top 100 eth receiving wallets
MATCH ()-[txn]->(w)
RETURN COALESCE(w.label, w.address) AS who,
       w.category AS ctgry,
       count(txn) AS sent_txn_count,
       ROUND(SUM(txn.num_tokens), 2) AS sent_tokens_total,
       ROUND(SUM(txn.num_tokens) / count(txn), 3) AS avg_tokens_per_txn
ORDER BY sent_tokens_total DESC
LIMIT 100


// Most common send/receive pathways by label
MATCH (w1)-[txn]->(w2)
RETURN w1.label, COUNT(txn) AS txn_count, w2.label
ORDER BY txn_count DESC


// Arrow of time query (All txions within 10 block_numbers of matched t0)
MATCH p=(w0)-[t0:TXN]->(w1)-[t1:TXN]->(w2)
WHERE t0.block_number < t1.block_number < t0.block_number +10
RETURN p limit 25


// Arrow of time query for all 3 hop paths for eth
MATCH path = ()-[txns:TXN * 3]->()
WHERE ALL(t IN txns WHERE t.token_address = '0x0') // All txns in path are eth txns
  AND ALL(i in range(0, size(txns) - 2) WHERE txns[i].block_number < txns[i + 1].block_number) // Time
RETURN path LIMIT 10


// Same as previous but show each hop individually instead of path
MATCH path = ()-[txns:TXN * 3]->()
WHERE ALL(t IN txns WHERE t.token_address = '0x0') // All txns in path are eth txns
  AND ALL(i in range(0, size(txns) - 2) WHERE txns[i].block_number < txns[i + 1].block_number) // Time
UNWIND range(0, size(txns) - 1) AS step_number
RETURN step_number, txns[step_number].token, txns[step_number].block_number,  txns[step_number].num_tokens
LIMIT 25


// See all the txions in sequence
MATCH paths = ()-[txns:TXN*3]->()
WHERE txns[0].block_number < txns[1].block_number < txns[2].block_number
  AND txns[0].token_address = txns[1].token_address = txns[2].token_address
UNWIND txns AS t
RETURN t LIMIT 25


// Row number query (maybe?)
MATCH (n:User)
WITH n
ORDER BY n.created_at
WITH collect(n) as users
UNWIND range(0, size(users)-1) as pos
SET (users[pos]).number = pos


// https://neo4j.com/developer/kb/comparing-relationship-properties-within-a-path/
MATCH path = (w0)-[txns:TXN * 10]->(w1)
WHERE w0.address = w1.address
  AND ALL(
    i in range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number
  )
RETURN size(txns) AS path_length, path
LIMIT 5


// Cycle detection query - cycles of length at most 5, with txns made up of at least 10.0 tokens
MATCH p=(w1)-[txns:TXN * 3..4]->(w1)
WHERE ALL(t in txns WHERE t.num_tokens > 100)
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number // Arrow of time
  )

WITH p AS p,
     txns AS txns,
     apoc.coll.duplicates([n IN nodes(p) | n.address]) AS duplicate_wallets
WHERE size(duplicate_wallets) = 0
RETURN p
LIMIT 1


// Around 7000 blocks per day, so this is cycles within a day
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


// Cycles with txns in 24 hours increments, with no crossovers
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


// Get paths out from possible celsius wallet
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
