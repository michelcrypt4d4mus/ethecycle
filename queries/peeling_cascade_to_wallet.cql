///////////////////////////////////////////////////////////////////////////////////////////////////////
// "Peeling cascade" (splitting up N tokens into smaller groups and routing through multiple wallets //
///////////////////////////////////////////////////////////////////////////////////////////////////////

// Explicit, two step path variable version of what is generalized below
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


// Generalized version of previous query re: Who funded '0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27'?
// Find similar time txions adding up to a certain $txn_size that could have ended in a particular wallet.
:param blocks_to_check => 10000;  // How many blocks before the final txns will we search
:param txn_size => 1000;  // Aggregate size of 'cascaded' txions
:param tolerance => 1.5;  // how much distance +/- from txn_size will we consider part of the cascade
:param min_txns_in_cascade => 1;
:param max_txns_in_cascade => 3;  // Query run time will get more expensive with higher values
:param min_txn_size => 1; // Don't look at txns for less tokens than this number
:param address_length => 9; // Just for printing
:param cascade_block_distance => 70;  // Txns must be within this many blocks of each to be considered part of cascade
:param max_blocks_between_cascades => 100;  // Max blocks between steps of the cascade

// Note that the maximum length of paths to look for (set to 5 here) must be hardcoded
MATCH ()-[txns:TXN * 5]->(celsius_wallet)
WHERE celsius_wallet.address = toLower('0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27')
  AND ALL(
        t in txns
    WHERE t.num_tokens >= $min_txn_size  // Over min size txn
      AND (txns[-1].block_number - $blocks_to_check) <= t.block_number <= txns[-1].block_number // in block range
  )
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number // Arrow of time
      AND txns[i + 1].block_number < (txns[i].block_number + $max_blocks_between_cascades) // Close enough blocks
  )

// What follows is a sort of pivot operation, where we want to build a list of lists
// with size(txns) elements. Each element is a list containing all the possible txns that
// could have happened at that step.
UNWIND range(0, size(txns) - 1) AS i  // "i" is the step number from here on out
// Create a list of 2-tuples: (step_number, list_of_possible_txns_at_step_number)
WITH collect([i, txns[i]]) AS step_n_possibilities

// Perform a DISTINCT call to strip out duplicates and lower computation complexity
// TODO: possible to do this in the previous step?
UNWIND step_n_possibilities AS step_n_possibility
WITH DISTINCT step_n_possibility[0] AS i,
     collect(DISTINCT step_n_possibility[1]) AS txns
WITH *,
     size(txns) AS txn_count,
     CASE size(txns) > $max_txns_in_cascade
        WHEN true THEN $max_txns_in_cascade
        ELSE size(txns) END AS max_txns

// Use apoc combinations() method to find all permutations for each step of a certain
// size. Our ultimate goal is to find sets of txns that happened at roughly the same time
// (specifically within $cascade_block_distance blocks of each other) and whose total
// number of tokens adds up to $txn_size.
WITH i AS i,
     apoc.coll.combinations(txns, $min_txns_in_cascade, max_txns) AS txn_groups
UNWIND txn_groups AS txn_group

// Total the num_tokens for each txn_group found by apoc.coll.combinations() and
// check the group happened within $cascade_block_distance blocks of each other
WITH i AS i,
     txn_group AS txn_group,
     reduce(tokens = 0, t in txn_group | tokens + t.num_tokens) AS num_tokens
WHERE ($txn_size + $tolerance) > num_tokens > ($txn_size - $tolerance)  // txn_group tokens add up to $txn_size
  AND ALL(
        i IN range(0, size(txn_group) - 2)
    // All txions being within N blocks of txn_group[-1] means they are within 2*N blocks of each other
    WHERE abs(txn_group[i].block_number - txn_group[-1].block_number) <= $cascade_block_distance
  )

RETURN i AS step,
        // List of abbreviations of wallet addresses and num_tokens. For readability more than anything.
        [
            t in txn_group |
            [
                SUBSTRING(STARTNODE(t).address, 0, $address_length),
                '=>',
                ROUND(t.num_tokens, 2),
                '=>',
                SUBSTRING(ENDNODE(t).address, 0, $address_length)
            ]
        ] AS possibile_sources,
       num_tokens AS total_tokens
