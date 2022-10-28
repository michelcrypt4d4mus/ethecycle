//////////////////////////////////////////////////////////////
// Wallets with in/out summing to $flow_size +/- $tolerance //
//////////////////////////////////////////////////////////////

// Find similar time txions adding up to a certain $txn_size that could have ended in a particular wallet.
:param start_block => 4109360; // 3990001;
:param end_block   => 4109392; // 4110000;
:param min_txn_size => 1; // Don't look at txns for less tokens than this number
:param flow_size => 1000;  // Aggregate size of 'cascaded' txions
:param tolerance => 10;  // how much distance +/- from txn_size will we consider part of the cascade
:param address_length => 9; // Just for printing
:param flow_window_blocks => 40;  // In and out txns must be within this many blocks


MATCH ()-[in_txn]->(w)-[out_txn]->()
WHERE $start_block <= in_txn.block_number <= $end_block // In block range
  AND $start_block <= out_txn.block_number <= $end_block // In block range
  AND in_txn.num_tokens >= $min_txn_size // Over min size txn
  AND out_txn.num_tokens >= $min_txn_size // Over min size txn
  AND 0 < (out_txn.block_number - in_txn.block_number) <= $flow_window_blocks // out_txn after in_txn by no more than $flow_window_blocks

// Create lists of distinct in and out txns
WITH collect(DISTINCT in_txn) AS in_txns,
     w AS w,
     collect(DISTINCT out_txn) AS out_txns

WITH reduce(tokens = 0, t in in_txns | tokens + t.num_tokens) AS in_tokens,
     size(in_txns) AS in_txn_count,
     w AS w,
     reduce(tokens = 0, t in out_txns | tokens + t.num_tokens) AS out_tokens,
     size(out_txns) AS out_txn_count

WHERE (in_tokens - $tolerance) <= $flow_size <= (in_tokens + $tolerance)
  AND (out_tokens - $tolerance) <= $flow_size <= (out_tokens + $tolerance)

RETURN in_tokens, in_txn_count, w.address, out_tokens, out_txn_count
