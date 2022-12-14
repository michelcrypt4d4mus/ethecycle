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
:param txn_size => 1001;  // Aggregate size of 'cascaded' txions
:param tolerance => 0.9;  // how much distance +/- from txn_size will we consider part of the cascade
:param min_txns_in_cascade => 1;
:param max_txns_in_cascade => 4;  // Query run time will get more expensive with higher values
:param min_txn_size => 0.95; // Don't look at txns for less tokens than this number
:param address_length => 9; // Just for printing
:param cascade_block_distance => 70;  // Txns must be within this many blocks of each to be considered part of cascade
:param max_blocks_between_cascades => 100;  // Max blocks between steps of the cascade

// Note that the maximum length of paths to look for (set to 5 here) must be hardcoded
// To get upstream txions:
//
// To get downstream, switch to:
//     MATCH (celsius_wallet)-[txns:TXN * 5]->(end_wallet)
MATCH ()-[txns:TXN * 7]->(celsius_wallet)
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
// could have happened at that step of the path.
UNWIND range(0, size(txns) - 1) AS i  // "i" is the step number from here on out
// Create a list of 2-tuples: (step_number, list_of_possible_txns_at_step_number)
WITH DISTINCT collect([i, txns[i]]) AS step_n_possibilities

UNWIND step_n_possibilities AS step_n_possibility
WITH DISTINCT step_n_possibility[0] AS i
    ,collect(DISTINCT step_n_possibility[1]) AS txns

WITH i AS i
    ,txns AS txns
    ,size(txns) AS txn_count
    ,CASE size(txns) > $max_txns_in_cascade
       WHEN true THEN $max_txns_in_cascade
       ELSE size(txns) END AS max_txns

// Use apoc combinations() method to find all permutations for each step of a certain size. Our
// ultimate goal is to find sets of txns that happened at roughly the same time (AKA within
// $cascade_block_distance blocks of each other) and whose tokens add up to $txn_size.
UNWIND apoc.coll.combinations(txns, $min_txns_in_cascade, max_txns) AS txn_group

// Total the num_tokens for each txn_group found by apoc.coll.combinations() and
// check the group happened within $cascade_block_distance blocks of each other
WITH i AS i
     ,txn_group AS txn_group
     ,reduce(tokens = 0, t in txn_group | tokens + t.num_tokens) AS num_tokens
     ,[t in txn_group | t.block_number] AS txn_block_numbers
WHERE ($txn_size + $tolerance) > num_tokens > ($txn_size - $tolerance)  // txn_group tokens add up to $txn_size
  AND txn_block_numbers[-1] - txn_block_numbers[0] <= $cascade_block_distance
// Less memory intensive (but less accurate - doubles the distance) way of doing the same block range clause:
//   AND ALL(
//         i IN range(0, size(txn_group) - 2)
//     // All txions being within N blocks of txn_group[-1] means they are within 2*N blocks of each other
//     WHERE abs(txn_group[i].block_number - txn_group[-1].block_number) <= $cascade_block_distance
//   )

// Add from_addresses to identify common source wallets only after we've identified valid txn_groups
// to avoid unnecessary calls to apoc.coll.toSet()
WITH *, apoc.coll.toSet([t in txn_group | STARTNODE(t).address ]) AS unique_from_addresses
// Optionally filter for only unique sources (drastically less output)
//WHERE size(unique_from_addresses) = 1

RETURN i AS step
       ,num_tokens AS tokens

        // List of abbreviations of wallet addresses and num_tokens. For readability more than anything.
       ,[
            t in txn_group |
            SUBSTRING(STARTNODE(t).address, 0, $address_length) +
                ' sent ' + ROUND(t.num_tokens, 3) +
                ' to ' + SUBSTRING(ENDNODE(t).address, 0, $address_length) +
                ' in block ' + t.block_number
        ] AS possible_sources

       // If all txns came from same wallet then put etherscan link, else just number of unique addresses
       ,CASE size(unique_from_addresses)
          WHEN 1 THEN 'https://etherscan.io/address/' + unique_from_addresses[0]
          ELSE '' + size(unique_from_addresses) + ' unique sources' END AS etherscan_link_for_single_sources

// Order by step first, then from least unique_from_addresses to most
ORDER BY step, size(unique_from_addresses)
