// Celsius 10 address: 0x917334942eEe7C32DcCcFbdE975F3e0ac30EfaC4

// Note that the maximum length of paths to look for (set to 5 here) must be hardcoded
MATCH path = (start_wallet)-[txns:TXN *2..7]->(celsius_wallet)
WHERE start_wallet.address = toLower('0x4Eb3Dd12ff56f13a9092bF77FC72C6EE77Ae9e27')
  AND celsius_wallet.address = toLower('0x917334942eee7c32dcccfbde975f3e0ac30efac4')
  //AND txns[-1].transaction_hash = '0xb2c0911099dbdb1b71663f3c47332199268c673943a925d78c2b96cbf35f0ddb'
  AND ALL(
        t in txns
    WHERE t.num_tokens >= $min_txn_size  // Over min size txn
      //AND (txns[-1].block_number - $blocks_to_check) <= t.block_number <= txns[-1].block_number // in block range
  )
  AND ALL(
        i IN range(0, size(txns) - 2)
    WHERE txns[i].block_number < txns[i + 1].block_number // Arrow of time
       //AND txns[i + 1].block_number < (txns[i].block_number + $max_blocks_between_cascades) // Close enough blocks
  )
RETURN path, txns
LIMIT 10

