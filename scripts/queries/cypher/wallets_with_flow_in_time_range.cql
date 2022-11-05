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
WHERE $start_block <= in_txn.block_number <= $end_block  // In block range
  AND $start_block <= out_txn.block_number <= $end_block // In block range
  AND in_txn.num_tokens >= $min_txn_size  // Over min size txn
  AND out_txn.num_tokens >= $min_txn_size // Over min size txn
  AND 0 < (out_txn.block_number - in_txn.block_number) <= $flow_window_blocks // out_txn after in_txn by <= $flow_window_blocks

// Create lists of distinct in and out txns
WITH collect(DISTINCT in_txn) AS in_txns,
     w AS w,
     collect(DISTINCT out_txn) AS out_txns

// Use reduce() to sum the inflow and outflow tokens
WITH reduce(tokens = 0, t in in_txns | tokens + t.num_tokens) AS in_tokens,
     size(in_txns) AS in_txn_count,
     in_txns,
     w AS w,
     reduce(tokens = 0, t in out_txns | tokens + t.num_tokens) AS out_tokens,
     size(out_txns) AS out_txn_count,
     out_txns

// Filter for wallets with inflow and outflow within $tolerance of $flow_size
WHERE (in_tokens - $tolerance) <= $flow_size <= (in_tokens + $tolerance)
  AND (out_tokens - $tolerance) <= $flow_size <= (out_tokens + $tolerance)

RETURN w.address,
       ROUND(in_tokens, 3) AS in_tokens,
       ROUND(out_tokens, 3) AS out_tokens,

       in_txn_count,
       out_txn_count,

       apoc.coll.min([t in in_txns | t.block_number]) AS first_block_in,
       apoc.coll.max([t in in_txns | t.block_number]) AS last_block_in,
       apoc.coll.min([t in out_txns | t.block_number]) AS first_block_out,
       apoc.coll.max([t in out_txns | t.block_number]) AS last_block_out,

       // List of strings showing from address, amount, and blocknumber of each in_txn
       [
            t in in_txns |
            'received ' + ROUND(t.num_tokens, 3) +
                ' from ' + SUBSTRING(STARTNODE(t).address, 0, $address_length) +
                ' in block ' + t.block_number
       ] AS in_txns_info,

       // List of strings showing to address, amount, and blocknumber of each out_txn
       [
            t in out_txns |
            'sent ' + ROUND(t.num_tokens, 3) +
                ' to ' + SUBSTRING(ENDNODE(t).address, 0, $address_length) +
                ' in block ' + t.block_number
       ] AS out_txns_info
