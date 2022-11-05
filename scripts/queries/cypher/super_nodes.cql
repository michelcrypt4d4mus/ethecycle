// Who is 0x02459d2ea9a008342d8685dae79d213f14a87d43
MATCH (from_w)-[txn]->(to_w)
WHERE from_w.address = '0x02459d2ea9a008342d8685dae79d213f14a87d43'

RETURN COALESCE(to_w.label, w.address) AS who,
       w.category AS ctgry,
       count(txn) AS sent_txn_count,
       ROUND(SUM(txn.num_tokens), 2) AS sent_tokens_total,
       ROUND(SUM(txn.num_tokens) / count(txn), 3) AS avg_tokens_per_txn
ORDER BY sent_tokens_total DESC
LIMIT 100

